# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enhancements',
    version='0.1.13',
    author='Manfred Kaiser',
    author_email='manfred.kaiser@logfile.at',
    description='utility library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="development configparser argparse",
    python_requires='>= 3.6',
    packages=find_packages(exclude=("tests",)),
    package_data={
        'enhancements': ['py.typed'],
    },
    url="https://enhancements.readthedocs.io/",
    project_urls={
        'Source': 'https://github.com/manfred-kaiser/python-enhancements',
        'Tracker': 'https://github.com/manfred-kaiser/python-enhancements/issues',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Development Status :: 5 - Production/Stable"
    ],
)
