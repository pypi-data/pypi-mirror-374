from setuptools import setup, find_packages

setup(
    name="vector_khing",               # Must be unique on PyPI!
    version="0.1.0",                # Follow semantic versioning
    description="This is my first project.Use to calculate dot product,cross product, and magnitude of vector.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="khing",
    author_email="anchitha2005@gmail.com",
    url="https://github.com/khing2005/vector_khing",  # optional
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)