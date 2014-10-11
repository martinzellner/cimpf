import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cimpf",
    version = "0.0.1",
    author = "Martin Zellner",
    author_email = "martin.zellner@gmail.com",
    description = ("A power-flow solver for CIM"),
    license = "",
    keywords = "",
    url = "https://github.com/murphy2",
    install_requires=[
          'PyCIM',
          'numpy'
      ],
    long_description=read('README.md'),
    classifiers=[
    ],
)