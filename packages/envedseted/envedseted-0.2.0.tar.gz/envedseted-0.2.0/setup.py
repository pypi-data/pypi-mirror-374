from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="envedseted",
    version="0.2.0",
    author="Catergems",
    author_email="supornthanaphat@gmail.com",
    description="Advanced environment variable manager with PATH support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThanaphatSuporn/envedseted",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "envedseted=envedseted.cli:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
