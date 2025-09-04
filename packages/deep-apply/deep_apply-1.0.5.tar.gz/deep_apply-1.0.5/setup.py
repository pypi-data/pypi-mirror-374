from setuptools import setup
from setuptools import find_packages

name = "deep-apply"
version = "1.0.5"

with open("README.md", "r") as f:
    long_description = f.read()

requires = []

setup(
    name=name,
    version=version,
    author="Zairon Jacobs",
    author_email="zaironjacobs@gmail.com",
    description="Deep traverse through an object and apply a function on its values.",
    long_description=long_description,
    url="https://github.com/zaironjacobs/deep-apply",
    download_url=f"https://github.com/zaironjacobs/deep-apply/archive/v{version}.tar.gz",
    keywords=[
        "deep",
        "traverse",
        "apply",
        "object",
        "list",
        "set",
        "tuple",
        "pydantic",
        "dict",
    ],
    packages=find_packages(),
    install_requires=requires,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: English",
    ],
    python_requires=">=3.11",
)
