from setuptools import setup, find_packages
with open("README.md", "r", encoding = "utf-8") as fh:
    long_description=fh.read()

setup(
    name="brs",
    version="1.0.0",
    packages=find_packages("brs"),
    install_requires=[
    ],
    author="TorbTorb",
    description="A python module for reading/creating/writing .brs files for Brickadia.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TorbTorb/brs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12"
)