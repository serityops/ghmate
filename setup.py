import os
from setuptools import setup, find_packages
from configparser import ConfigParser

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

config = ConfigParser()
config.read('setup.cfg')

setup(
    name=config.get('metadata', 'name'),
    version=config.get('metadata', 'version'),
    description=config.get('metadata', 'description'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/serityops/ghmate',
    license=config.get('metadata', 'license'),
    license_files=config.get('metadata', 'license_files').split('\n'),
    packages=find_packages(),
    classifiers=config.get('metadata', 'classifiers').split('\n'),
    python_requires='>=3.8'
)
