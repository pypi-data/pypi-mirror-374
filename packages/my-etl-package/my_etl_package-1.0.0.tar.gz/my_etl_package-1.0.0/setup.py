from setuptools import setup, find_packages
import io
import os


# Read README.md for the long description
with io.open(
    os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="my_etl_package",
    version="1.0.0",
    description="A package for ETL pipeline operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Khaled Ahmed",
    author_email="khhaledahmaad@gmail.com",
    packages=find_packages(include=["my_etl_package", "my_etl_package.*"]),
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv",
        "numpy",
        "pandas",
        "sqlalchemy",
        "psycopg2-binary",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
