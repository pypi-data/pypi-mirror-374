#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "XDT (Exact Decision Tree) - High-performance decision tree classifier with exact split optimization"

# Read version from the main module
def get_version():
    version = "1.0.1"
    return version

setup(
    name="xdtclassifier",
    version=get_version(),
    author="mohdadil",
    author_email="mohdadil@live.com",
    description="XDT (Exact Decision Tree) - High-performance decision tree classifier with exact split optimization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nqmn/xdt",
    packages=find_packages(),
    py_modules=["xdt"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        "numba>=0.56.0",
        "psutil>=5.8.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "benchmark": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
        ],
    },
    keywords="machine-learning decision-tree classification xdt exact-splits histogram optimization",
    project_urls={
        "Bug Reports": "https://github.com/nqmn/xdt/issues",
        "Source": "https://github.com/nqmn/xdt",
        "Documentation": "https://github.com/nqmn/xdt#readme",
    },
    zip_safe=False,
    include_package_data=True,
)