from platform import python_revision

from setuptools import setup, find_packages

setup(
    name= "Python-Perceptron",
    version="0.1.0",
    author="ml engineer",
    author_email="bktashfany46@gmail.com",
    description="A simple Python library for perceptron simulation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bktashebadi/Perceptron",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)