"""
Setup script for excel2pyral package.

This file provides compatibility with older Python packaging tools
that don't support PEP 621 (pyproject.toml).
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'excel2pyral', '__init__.py')
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.1.4"

# Read README for long description
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="excel2pyral",
    version=get_version(),
    description="Convert Excel register specifications to PyUVM RAL models via SystemRDL",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Sanjay Singh",
    include_package_data=True,
    author_email="your.email@example.com",
    url="https://github.com/SanCodex/excel2pyral",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "systemrdl-compiler>=1.27.0",
        "pyuvm>=2.8.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8", 
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyral=excel2pyral.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    keywords="SystemRDL PyUVM RAL Register Excel UVM",
    project_urls={
        "Bug Reports": "https://github.com/SanCodex/excel2pyral/issues",
        "Source": "https://github.com/SanCodex/excel2pyral",
        "Documentation": "https://github.com/SanCodex/excel2pyral/blob/main/README.md",
    },
)
