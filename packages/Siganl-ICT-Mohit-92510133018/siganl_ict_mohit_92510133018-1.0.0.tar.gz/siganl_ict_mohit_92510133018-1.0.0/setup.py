"""
Setup script for signal_ICT_StudentName_EnrollmentNo package

This script enables the package to be built into wheel (.whl) and 
source distribution (.tar.gz) files for distribution.
"""

from setuptools import setup, find_packages

# Read README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

except FileNotFoundError:
    long_description = "A Python package for signal generation and operations"

setup(
    name="Siganl_ICT_Mohit_92510133018",
    version="1.0.0",
    author="Mohit Parekh",
    author_email="mohit.parekh141006@marwadiuniversity.ac.in",
    description="A Python package for fundamental signal processing operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sonimohit11/Siganl_ICT_Mohit_92510133018",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Education",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "signal-demo=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)