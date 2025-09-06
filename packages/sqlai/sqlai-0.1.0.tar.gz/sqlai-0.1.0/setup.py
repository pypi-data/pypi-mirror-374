# setup.py
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sqlai",
    version="0.1.0",
    author="Alexander Brück",
    description="A command-line tool for SQL AI queries",
    long_description=long_description,
    url="https://github.com/alexanderbrueck/sqlai",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=["google-generativeai==0.8.5", "tomli==2.2.1", "tomli_w==1.2.0"],
    entry_points={
        "console_scripts": [
            "sqlai=sqlai.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
)
