from setuptools import setup, find_packages

setup(
    name="stvtermux",
    version="1.0.1",
    description="STV Login & Register system for Termux",
    author="Trọng Phúc",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "stv=stvtermux.cli:main"
        ]
    },
)