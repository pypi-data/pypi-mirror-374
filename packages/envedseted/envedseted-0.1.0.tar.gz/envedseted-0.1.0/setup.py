from setuptools import setup, find_packages

setup(
    name="envedseted",
    version="0.1.0",
    description="Set, update, delete, and list environment variables (user or system)",
    author="Catergems",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "envedseted=envedseted.cli:main"
        ],
    },
    python_requires=">=3.7",
)
