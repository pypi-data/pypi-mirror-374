from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="stakepd",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)
