# setup.py

from setuptools import setup, find_packages

setup(
    name="uhd_client",
    version="1.1.1",
    author="Ojas Gupta",
    description="A Python client for XplainDB",
    long_description="A simple, intuitive client for interacting with a XplainDB server, handling SQL, NoSQL, Graph, and Vector operations.",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)