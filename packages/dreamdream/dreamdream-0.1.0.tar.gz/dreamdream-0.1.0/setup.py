# setup.py
from setuptools import setup, find_packages

setup(
    name="dreamdream",               # pip install dreamdream
    version="0.1.0",
    description="asdasd",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    packages=find_packages(),        # test 포함
    scripts=["run.py"],
    python_requires=">=3.7",
)