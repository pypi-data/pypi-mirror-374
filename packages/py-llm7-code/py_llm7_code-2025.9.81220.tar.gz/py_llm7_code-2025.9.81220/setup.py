from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py_llm7_code",
    version="2025.9.81220",
    author="Eugene Evstafev",
    author_email="chigwel@gmail.com",
    description="LLM7-powered generator that creates a minimal single-function Python package and runner from a natural-language spec.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chigwell/py_llm7_code",
    project_urls={
        "Source": "https://github.com/chigwell/py_llm7_code",
        "Tracker": "https://github.com/chigwell/py_llm7_code/issues",
    },
    packages=find_packages(),
    install_requires=[
        "langchain-core",
        "langchain-llm7",
        "llmatch-messages",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    license="MIT",
    tests_require=["unittest"],
    test_suite="test",
    include_package_data=True,
    zip_safe=False,
)
