from setuptools import setup, find_packages

setup(
    name="stvtermux",
    version="1.0.8",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "stv=stvtermux.cli:main",
        ],
    },
)