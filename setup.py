# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enhancements',
    version='0.0.10',
    author='Manfred Kaiser',
    author_email='manfred.kaiser@logfile.at',
    description='utility library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>= 3.5',
    packages=find_packages(exclude=("tests",)),
    url="https://enhancements.readthedocs.io/",
    project_urls={
        'Source': 'https://github.com/manfred-kaiser/python-enhancements',
        'Tracker': 'https://github.com/manfred-kaiser/python-enhancements/issues',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
)
