from setuptools import setup, find_packages

setup(
    name="pyforth",
    version="0.1.0",
    description="A simple stack-based Forth interpreter in Python",
    author="UndrDsk0M",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pyforth=pyforth.pyforth:main"
        ]
    },
    python_requires=">=3.7",
)