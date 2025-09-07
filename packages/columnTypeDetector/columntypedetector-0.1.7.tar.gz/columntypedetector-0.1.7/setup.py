import os
from setuptools import setup, find_packages

# Get the directory where setup.py is located
here = os.path.abspath(os.path.dirname(__file__))

# Read the README file for the long description
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="columnTypeDetector",
    version="0.1.7",
    description="Detect types of columns in delimited files using DuckDB and pandas",
    author="Vikas Bhaskar Vooradi",
    author_email="vikasvooradi.developer@gmail.com",
    packages=find_packages(),
    install_requires=[
        "duckdb>=1.3.2",
        "pandas>=2.1.4",
    ],
    python_requires=">=3.12.3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=("LICENSE",),
)
