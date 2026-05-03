from setuptools import setup, find_packages

setup(
    name="ghostdumper",
    version="2.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ghostdump=ghostdumper.cli:main",
        ],
    },
)
