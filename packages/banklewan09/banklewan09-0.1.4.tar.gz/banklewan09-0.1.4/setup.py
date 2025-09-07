from setuptools import setup, find_packages

setup(
    name="banklewan09",               # Must be unique on PyPI!
    version="0.1.4",                # Follow semantic versioning
    description="This is my first package. This package are calculation volume ,lateral and surface in cylinder .",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lewan",
    author_email="natthapong.nn@mail.wu.ac.th",
    url="https://github.com/yourusername/mypackage",  # optional
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)