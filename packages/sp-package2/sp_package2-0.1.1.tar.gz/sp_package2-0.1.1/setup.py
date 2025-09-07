from setuptools import setup, find_packages

setup(
    name="sp_package2",               # Must be unique on PyPI!
    version="0.1.1",                # Follow semantic versioning
    description="A simple example package with basic calculation of sphere.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yok",
    author_email="raseljone.com@gmail.com",
    url="https://github.com/paytai/sp_package",  # optional
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)