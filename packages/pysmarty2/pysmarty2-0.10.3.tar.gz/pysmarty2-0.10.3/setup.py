"""Setup for pysmarty2 package."""

import os
import setuptools

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# Ensure requirements.txt exists before reading it
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as f:
        REQUIREMENTS = [line.strip() for line in f if line.strip()]
else:
    REQUIREMENTS = []


setuptools.setup(
    name="pysmarty2",
    version="0.10.3",
    author="Martins Sipenko, Theo Nicolaum",
    author_email="martins.sipenko@gmail.com",
    description="Python API for Salda Smarty Modbus TCP",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/martinssipenko/pysmarty2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=list(val.strip() for val in open('requirements.txt')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
