from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

with open("LICENSE", "r") as f:
    license_text = f.read()

setup(
    name="columnTypeDetector",
    version="0.1.5",
    description="Detect types of columns in delimited files using DuckDB and pandas",
    author="Vikas Bhaskar Vooradi",
    author_email="vikasvooradi.developer@gmail.com",  
    packages=find_packages(),
    install_requires=["duckdb>=1.3.2", "pandas>=2.1.4"],
    python_requires=">=3.12.3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description=description,
    long_description_content_type="text/markdown",
    license="MIT", 
    license_files=("LICENSE",),
    
)

