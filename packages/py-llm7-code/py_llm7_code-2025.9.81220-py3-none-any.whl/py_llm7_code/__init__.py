# orchestrator.py
from __future__ import annotations

import contextlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional/posix-only; guarded during use
try:
    import resource as _resource  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    _resource = None  # type: ignore[assignment]

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_llm7 import ChatLLM7
from llmatch_messages import llmatch


def generate_package_with_llm7(
    llm: ChatLLM7(base_url="https://api.llm7.io/v1"),
    spec_text: str,
    *,
    package_name: str | None = None,
    max_retries: int = 10,
    exec_timeout_sec: int = 8,
    memory_limit_mb: int = 256,
    verbose: bool = False,
    pip_packages: Optional[List[str]] = None,
    allowed_imports: Optional[List[str]] = None,
    pip_index_url: Optional[str] = None,
    pip_extra_index_urls: Optional[List[str]] = None,
    pip_no_deps: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrate LLM7 codegen → extraction → file write → safety checks →
    syntax/import checks → sandboxed execution with timeout/memory limits →
    optional venv creation + pip install → retry on failure.

    Args:
        llm: ChatLLM7 instance.
        spec_text: Natural language spec for the package.
        package_name: Optional desired package name.
        max_retries: Retry attempts for model/code execution.
        exec_timeout_sec: Timeout for running generated code.
        memory_limit_mb: Soft memory limit for execution (POSIX best-effort).
        verbose: Include attempts/debug info in the result.
        pip_packages: Pip requirement strings to install in an isolated venv,
            e.g. ["langchain-llm7==0.5.0"].
        allowed_imports: Python import module names allowed for third-party
            imports in generated code, e.g. ["langchain_llm7"].
        pip_index_url: Optional custom index URL.
        pip_extra_index_urls: Optional extra index URLs.
        pip_no_deps: Pass --no-deps to pip install.

    Returns:
        Dict with success flag, code, stdout/stderr, etc.
    """

    def _venv_paths(venv_dir: Path) -> Tuple[Path, Path]:
        if os.name == "nt":
            py = venv_dir / "Scripts" / "python.exe"
            pip = venv_dir / "Scripts" / "pip.exe"
        else:
            py = venv_dir / "bin" / "python"
            pip = venv_dir / "bin" / "pip"
        return py, pip

    def _create_venv(venv_dir: Path) -> Tuple[bool, str, str, Optional[Path], Optional[Path]]:
        cmd = [sys.executable, "-m", "venv", str(venv_dir)]
        ok, out, err = _run(cmd)
        if not ok:
            return False, out, err, None, None
        py, pip = _venv_paths(venv_dir)
        return True, out, err, py, pip

    def _pip_install(
        pip_exe: Path,
        requirements: List[str],
        *,
        index_url: Optional[str],
        extra_indexes: Optional[List[str]],
        no_deps: bool,
    ) -> Tuple[bool, str, str]:
        if not requirements:
            return True, "", ""

        cmd = [str(pip_exe), "install", "--disable-pip-version-check", "--no-input"]
        if no_deps:
            cmd.append("--no-deps")
        if index_url:
            cmd += ["--index-url", index_url]
        for url in extra_indexes or []:
            cmd += ["--extra-index-url", url]
        cmd += requirements
        return _run(cmd)

    # ---------- helpers (inner to keep exactly one top-level function) ----------
    def _slugify(text: str, fallback: str = "genpkg") -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
        if not s:
            return fallback
        # Must be a valid identifier for package dir
        if not re.match(r"^[a-z_][a-z0-9_]*$", s):
            s = f"p_{s}"
        return s[:64]

    def _messages(user_payload: str) -> List[Any]:
        # As per spec: strict tags, no explanations outside tags
        sys_msg = SystemMessage(
            content=(
                "You are a senior Python code generator. Produce a minimal Python package "
                "with exactly one public function in __init__.py. Also produce either a run "
                "command or a runner script to demonstrate executing the function. "
                "Follow the output format strictly using XML-like tags. Do not include "
                "explanations outside the tags."
            )
        )
        user_msg = HumanMessage(content=[{"type": "text", "text": user_payload}])
        return [sys_msg, user_msg]

    def _build_user_payload(spec_: str, feedback: str | None) -> str:
        allowed = ", ".join(allowed_imports or [])
        ext_clause = (
            f"- External imports allowed: {allowed} (and stdlib). No other third-party imports.\n"
            if allowed
            else "- Pure Python, stdlib only.\n"
        )
        base = (
            "Specification:\n{spec}\n\n"
            "Constraints:\n"
            "- Package must contain exactly one function in **init**.py.\n"
            "- The package name is \"{pkg_name}\" — use it in any import/usage examples.\n"
            "- The function name must be snake_case and have a clear, self-contained docstring.\n"
            "- No network calls, file writes outside CWD, or subprocesses.\n"
            f"{ext_clause}"
            "- Provide minimal usage demonstration.\n\n"
            "Return strictly in this format with three sections:\n"
            "<init_py>`python\n# __init__.py\n# your code here\n`</init_py>\n"
            "<runner_py>`python\n# run.py\n# your code here (optional if run_cmd present)\n`</runner_py>\n"
            "<run_cmd>python run.py</run_cmd>\n"
        ).format(spec=spec_.strip(), pkg_name=pkg_name)
        if feedback:
            base += (
                "\nPrevious attempt failed due to:\n"
                f"{feedback}\n"
                "Traceback/Error (if any):\n"
                "{stderr_will_be_included_here}\n"
                "Please correct and re-output all three sections."
            )
        return base

    def _extract_with_llmatch(
        messages: List[Any],
        primary_pat: str,
        fallback_pat: str,
        verbose_flag: bool,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        # First attempt: strict fenced pattern
        resp1 = llmatch(
            llm=llm,
            messages=messages,
            pattern=primary_pat,
            verbose=verbose_flag,
        )
        if resp1.get("success"):
            return True, resp1.get("extracted_data", "")[0], resp1
        # Fallback: permissive tag-only pattern
        resp2 = llmatch(
            llm=llm,
            messages=messages,
            pattern=fallback_pat,
            verbose=verbose_flag,
        )
        if resp2.get("success"):
            return True, resp2.get("extracted_data", "")[0], resp2
        return False, "", resp2 if resp2 else resp1

    def _scan_prohibited(code: str) -> Optional[str]:
        bad_imports = [
            r"^\s*import\s+subprocess\b",
            r"^\s*from\s+subprocess\s+import\b",
            r"os\.system\s*\(",
            r"^\s*import\s+socket\b",
            r"^\s*from\s+socket\s+import\b",
            r"^\s*import\s+requests\b",
            r"^\s*from\s+requests\s+import\b",
            r"^\s*import\s+urllib\b",
            r"^\s*from\s+urllib\s+import\b",
            r"^\s*import\s+http\.client\b",
            r"^\s*from\s+http\.client\s+import\b",
            r"^\s*import\s+ftplib\b",
            r"^\s*from\s+ftplib\s+import\b",
            r"^\s*import\s+paramiko\b",
            r"^\s*from\s+paramiko\s+import\b",
        ]
        for pat in bad_imports:
            if re.search(pat, code, flags=re.MULTILINE):
                return f"Prohibited import/pattern detected: {pat}"
        return None

    def _top_level_defs_only_one(code: str) -> Optional[str]:
        if re.search(r"(?m)^\s*class\s+\w+\s*:", code):
            return "Classes are not allowed in __init__.py."
        defs = re.findall(r"(?m)^def\s+\w+\s*\(", code)
        if len(defs) != 1:
            return f"Expected exactly one top-level function, found {len(defs)}."
        return None

    def _normalize_code(s: str) -> str:
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        s = s.lstrip("\ufeff")
        return s

    def _write_file(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _py_compile_check(py_exe: str, files: List[Path]) -> Tuple[bool, str, str]:
        cmd = [py_exe, "-m", "py_compile"] + [str(p) for p in files]
        return _run(cmd)

    def _import_check(py_exe: str, pkg_dir: Path, pkg_name_: str) -> Tuple[bool, str, str]:
        code = textwrap.dedent(
            f"""
            import sys, importlib, inspect
            sys.path.insert(0, {str(pkg_dir.parent)!r})
            m = importlib.import_module({pkg_name_!r})
            funcs = [o for o in m.__dict__.values() if inspect.isfunction(o) and o.__module__ == {pkg_name_!r}]
            assert len(funcs) == 1, f"Expected 1 function, got {{len(funcs)}}"
            """
        ).strip()
        cmd = [py_exe, "-c", code]
        return _run(cmd, cwd=pkg_dir.parent)

    def _validate_run_cmd_str(run_cmd_str: str) -> Tuple[bool, str, List[str]]:
        if not run_cmd_str.strip():
            return False, "Empty run_cmd.", []
        toks = shlex.split(run_cmd_str, posix=True)
        if not toks:
            return False, "run_cmd parsed to empty tokens.", []
        if toks[0] != "python":
            return (
                False,
                "run_cmd must start with 'python' per constraints.",
                [],
            )
        # Reject obviously unsafe patterns in '-c' payload, if any
        if "-c" in toks:
            try:
                idx = toks.index("-c")
                snippet = toks[idx + 1] if idx + 1 < len(toks) else ""
            except ValueError:
                snippet = ""
            if _scan_prohibited(snippet):
                return False, "Prohibited pattern inside run_cmd -c snippet.", []
        # Replace 'python' with current interpreter for reliability
        toks[0] = sys.executable
        return True, "", toks

    def _auto_minimal_run(py_exe: str, pkg_dir: Path, pkg_name_: str) -> List[str]:
        code = textwrap.dedent(
            f"""
            import sys, import importlib, inspect, json
            sys.path.insert(0, {str(pkg_dir.parent)!r})
            m = importlib.import_module({pkg_name_!r})
            f = next(v for k, v in m.__dict__.items() if inspect.isfunction(v) and v.__module__ == {pkg_name_!r})
            import inspect as _i
            sig = _i.signature(f)
            can_call = all(
                p.default is not _i._empty or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                for p in sig.parameters.values()
            )
            if can_call:
                try:
                    rv = f()
                    print(json.dumps({{"result": rv}}, ensure_ascii=False))
                except TypeError:
                    # If args are required without defaults, just print function name
                    print(json.dumps({{"function": f.__name__}}))
            else:
                print(json.dumps({{"function": f.__name__}}))
            """
        ).strip()
        return [py_exe, "-c", code]

    def _prepare_env(base_dir: Path) -> Dict[str, str]:
        env = {
            "PYTHONPATH": str(base_dir),
            "PYTHONNOUSERSITE": "1",
            "PATH": os.environ.get("PATH", ""),
        }
        return env

    def _set_limits():
        if _resource is None:
            return
        # Address space & data segment (best-effort)
        try:
            bytes_limit = int(memory_limit_mb) * 1024 * 1024
            for rsrc in ("RLIMIT_AS", "RLIMIT_DATA"):
                if hasattr(_resource, rsrc):
                    lim = getattr(_resource, rsrc)
                    _resource.setrlimit(lim, (bytes_limit, bytes_limit))
        except Exception:
            pass

    def _make_runner(pkg_name_: str) -> str:
        return textwrap.dedent(
            f"""
            # run.py
            import os
            import sys
            import json
            import importlib
            import inspect

            # Ensure the package under this temp directory is importable
            sys.path.insert(0, os.path.dirname(__file__))

            m = importlib.import_module("{pkg_name_}")
            f = next(
                v
                for v in m.__dict__.values()
                if inspect.isfunction(v) and v.__module__ == "{pkg_name_}"
            )

            sig = inspect.signature(f)
            can_call = all(
                p.default is not inspect._empty
                or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                for p in sig.parameters.values()
            )

            if can_call:
                try:
                    rv = f()
                    print(json.dumps({{"result": rv}}, ensure_ascii=False))
                except TypeError:
                    # Function requires args without defaults
                    print(json.dumps({{"function": f.__name__}}))
            else:
                print(json.dumps({{"function": f.__name__}}))
            """
        ).lstrip()

    def _unwrap_code_block(s: str) -> str:
        t = (s or "").strip()

        # Triple-fenced block
        if t.startswith("```"):
            lines = t.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
            return "\n".join(lines)

        # Single backtick fence with optional language
        m = re.match(r"^`(?:[a-zA-Z0-9_+-]+)?\s*\n?(.*)\n?`$", t, flags=re.DOTALL)
        if m:
            return m.group(1).strip("\n")

        return t

    def _run(
        cmd: List[str],
        cwd: Optional[Path] = None,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> Tuple[bool, str, str]:
        env = _prepare_env(base_dir if "base_dir" in locals() else Path.cwd())
        if extra_env:
            env.update(extra_env)
        kwargs: Dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "cwd": str(cwd) if cwd else None,
            "env": env,
            "close_fds": True,
            "shell": False,
            "start_new_session": True,
        }
        if os.name == "posix":
            kwargs["preexec_fn"] = _set_limits  # type: ignore[assignment]
        try:
            p = subprocess.Popen(cmd, **kwargs)  # type: ignore[arg-type]
            try:
                out, err = p.communicate(timeout=exec_timeout_sec)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(Exception):
                    p.kill()
                out, err = p.communicate()
                return False, out, f"Timeout after {exec_timeout_sec}s.\n{err}"
            success = p.returncode == 0
            return success, out, err
        except Exception as e:
            return False, "", f"Subprocess error: {e}\n{traceback.format_exc()}"

    # ------------------------------- main flow ---------------------------------
    attempts: List[Dict[str, Any]] = []
    pkg_name = (package_name or _slugify(spec_text) or "genpkg").strip()
    base_dir = Path(tempfile.mkdtemp(prefix="llm7_genpkg_")).resolve()
    pkg_dir = base_dir / pkg_name
    init_path = pkg_dir / "__init__.py"
    run_path = base_dir / "run.py"

    primary_patterns = {
        "init_py": r"(?s)<init_py>\s*(.*?)\s*</init_py>",
        "runner_py": r"(?s)<runner_py>\s*(.*?)\s*</runner_py>",
        "run_cmd": r"(?s)<run_cmd>\s*(.*?)\s*</run_cmd>",
    }
    fallback_patterns = primary_patterns

    last_error = "Unknown error."
    extracted_last = {"init_py": "", "runner_py": "", "run_cmd": ""}

    for attempt_idx in range(1, int(max_retries) + 1):
        feedback = None if attempt_idx == 1 else last_error
        user_payload = _build_user_payload(spec_text, feedback)
        msgs = _messages(user_payload)

        # Extract sections with llmatch (primary + fallback)
        att: Dict[str, Any] = {
            "prompt_messages": [m.content for m in msgs] if verbose else None,
            "raw_response": "",  # llmatch doesn't guarantee raw; keep for schema
            "extracted": {"init_py": "", "runner_py": "", "run_cmd": ""},
            "validation": {
                "wrote_files": [],
                "syntax_ok": False,
                "import_ok": False,
                "exec_ok": False,
                "stdout": "",
                "stderr": "",
                "error": "",
            },
        }

        ok_init, init_code, resp_init = _extract_with_llmatch(
            msgs, primary_patterns["init_py"], fallback_patterns["init_py"], verbose
        )
        ok_runpy, runner_code, resp_runpy = _extract_with_llmatch(
            msgs, primary_patterns["runner_py"], fallback_patterns["runner_py"], verbose
        )
        ok_runcmd, run_cmd_str, resp_runcmd = _extract_with_llmatch(
            msgs, primary_patterns["run_cmd"], fallback_patterns["run_cmd"], verbose
        )

        # Remember best-known extracted values
        init_code = _normalize_code(init_code or "").strip()
        runner_code = _normalize_code(runner_code or "").strip()
        init_code = _unwrap_code_block(init_code)
        runner_code = _unwrap_code_block(runner_code)

        run_cmd_str = (run_cmd_str or "").strip()
        extracted_last = {
            "init_py": init_code,
            "runner_py": runner_code,
            "run_cmd": run_cmd_str,
        }
        att["extracted"] = dict(extracted_last)

        # Validate presence of init code
        if not ok_init or not init_code:
            last_error = "Missing <init_py> section or empty content."
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        venv_dir = base_dir / ".venv"
        py_exe: Path = Path(sys.executable)
        pip_exe: Optional[Path] = None

        # Create venv + install requested pip packages (if any)
        if pip_packages:
            ok, vout, verr, vpy, vpip = _create_venv(venv_dir)
            if not ok or vpy is None or vpip is None:
                return {
                    "success": False,
                    "attempt_count": 0,
                    "package_dir": str(base_dir),
                    "package_name": pkg_name,
                    "init_py_code": "",
                    "runner_code": "",
                    "run_cmd": "",
                    "stdout": vout,
                    "stderr": verr,
                    "error_message": "Failed to create venv.",
                }
            py_exe, pip_exe = vpy, vpip

            iok, iout, ierr = _pip_install(
                pip_exe,
                pip_packages,
                index_url=pip_index_url,
                extra_indexes=pip_extra_index_urls,
                no_deps=pip_no_deps,
            )
            if not iok:
                return {
                    "success": False,
                    "attempt_count": 0,
                    "package_dir": str(base_dir),
                    "package_name": pkg_name,
                    "init_py_code": "",
                    "runner_code": "",
                    "run_cmd": "",
                    "stdout": iout,
                    "stderr": ierr,
                    "error_message": "pip install failed.",
                }

        # Safety scans
        err = _scan_prohibited(init_code)
        if err:
            last_error = err
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        if runner_code:
            err2 = _scan_prohibited(runner_code)
            if err2:
                last_error = err2
                att["validation"]["error"] = last_error
                attempts.append(att)
                time.sleep(0.5 * attempt_idx)
                continue

        # Exactly one top-level function
        err = _top_level_defs_only_one(init_code)
        if err:
            last_error = err
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        # Write files
        wrote: List[str] = []
        try:
            _write_file(init_path, init_code)
            wrote.append(str(init_path))

            runner_code_effective = _make_runner(pkg_name)
            _write_file(run_path, runner_code_effective)
            wrote.append(str(run_path))
        except Exception as e:
            last_error = f"Failed to write files: {e}"
            att["validation"]["error"] = last_error
            att["validation"]["wrote_files"] = wrote
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        att["validation"]["wrote_files"] = wrote

        # Syntax check
        syn_ok, syn_out, syn_err = _py_compile_check(str(py_exe), [init_path] + ([run_path] if run_path.exists() else []))
        att["validation"]["syntax_ok"] = bool(syn_ok)
        if not syn_ok:
            last_error = f"Syntax error during py_compile.\n{syn_err}"
            att["validation"]["stderr"] = syn_err
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        # Import check
        imp_ok, imp_out, imp_err = _import_check(str(py_exe), pkg_dir, pkg_name)
        att["validation"]["import_ok"] = bool(imp_ok)
        if not imp_ok:
            last_error = f"Import check failed.\n{imp_err}"
            att["validation"]["stderr"] = imp_err
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        # Execution step
        if run_path.exists():
            exec_cmd = [str(py_exe), str(run_path.name)]
            cwd = base_dir
        elif run_cmd_str:
            valid, why, toks = _validate_run_cmd_str(run_cmd_str)
            if not valid:
                exec_cmd = _auto_minimal_run(str(py_exe), pkg_dir, pkg_name)
                cwd = base_dir
            else:
                toks[0] = str(py_exe)  # force venv python
                exec_cmd = toks
                cwd = base_dir
        else:
            exec_cmd = _auto_minimal_run(str(py_exe), pkg_dir, pkg_name)
            cwd = base_dir

        ex_ok, ex_out, ex_err = _run(exec_cmd, cwd=cwd)
        att["validation"]["exec_ok"] = bool(ex_ok)
        att["validation"]["stdout"] = ex_out
        att["validation"]["stderr"] = ex_err

        if not ex_ok:
            last_error = f"Execution failed.\n{ex_err or ex_out}"
            att["validation"]["error"] = last_error
            attempts.append(att)
            time.sleep(0.5 * attempt_idx)
            continue

        # Success
        result: Dict[str, Any] = {
            "success": True,
            "attempt_count": attempt_idx,
            "package_dir": str(base_dir),
            "package_name": pkg_name,
            "init_py_code": init_code,
            "runner_code": runner_code_effective,
            "run_cmd": " ".join(exec_cmd),
            "stdout": ex_out,
            "stderr": ex_err,
            "pip_packages_installed": pip_packages or [],
            "venv_python": str(py_exe),
        }
        if verbose:
            result["attempts"] = attempts + [att]
        return result

    # All attempts failed
    fail_result: Dict[str, Any] = {
        "success": False,
        "attempt_count": max_retries,
        "package_dir": str(base_dir),
        "package_name": pkg_name,
        "init_py_code": extracted_last.get("init_py", ""),
        "runner_code": extracted_last.get("runner_py", ""),
        "run_cmd": extracted_last.get("run_cmd", ""),
        "stdout": "",
        "stderr": "",
        "error_message": last_error,
    }
    if verbose:
        fail_result["attempts"] = attempts
    return fail_result
