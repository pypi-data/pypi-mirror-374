from setuptools import setup, find_packages
from pathlib import Path
import os

# Read version from version.py
version = {}
with open("fmp4j/version.py") as fp:
    exec(fp.read(), version)

# Find all package data files (non-Python files)
def find_package_data(package, directory):
    paths = []
    for (path, directories, filenames) in os.walk(os.path.join(package, directory)):
        for filename in filenames:
            paths.append(os.path.relpath(os.path.join(path, filename), package))
    return paths

setup(
    name="fmp4j",
    version=version["__version__"],
    description="Thin Python wrapper around the fmp4j Java SDK",
    long_description="TODO",
    long_description_content_type="text/markdown",
    author="Sorn Maksumic",
    author_email="sorn@sorn.dev",
    packages=find_packages(),
    package_data={
        "fmp4j": find_package_data("fmp4j", "typings") + ["version.py"]
    },
    install_requires=[
        "jpype1>=1.4.1",
        "urllib3>=1.26.9"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    entry_points={
        "console_scripts": [
            "fmp4j-check=fmp4j.cli:check_jvm",
        ],
    },
)