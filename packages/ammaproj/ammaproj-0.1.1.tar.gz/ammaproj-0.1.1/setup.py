from setuptools import setup, find_packages

setup(
    name="ammaproj",               # Must be unique on PyPI!
    version="0.1.1",                # Follow semantic versioning
    description="This is my first package . A simple example package to discribes Triangle.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="N. Amarittabut",
    author_email="nabeel65010@email.com",
    url="https://github.com/Amarit1008/AmaritPg",  # optional
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
)