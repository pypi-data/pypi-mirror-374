from setuptools import setup, find_packages  # type: ignore

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="dio-simple-package-project",
    version="0.0.1",
    author="Francisco Ricardo",
    author_email="fricardo@outlook.com",
    description="Example project for creating a simple package - DIO Course",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fricardo-it/dio-simple-package-project.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)
