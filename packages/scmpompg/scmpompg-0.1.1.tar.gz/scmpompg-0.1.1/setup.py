from setuptools import setup, find_packages

setup(
    name="scmpompg",      # Must be unique on PyPI!
    version="0.1.1",      # Follow semantic versioning
    description="This is my first package. This package is related to number theory.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="A. Karnbanjong",
    author_email="kpadisak@gmail.com",
    url="https://github.com/kadisak/scmpompg",  # optional
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
)