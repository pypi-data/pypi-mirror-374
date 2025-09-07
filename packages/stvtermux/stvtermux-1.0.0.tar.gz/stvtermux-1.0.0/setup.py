from setuptools import setup, find_packages

setup(
    name="STVTermux",
    version="1.0.0",
    description="STV Login & Register system for Termux",
    author="Phúc Trọng",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "stv=stvtermux.cli:main"
        ]
    },
)