import os
from setuptools import setup, find_packages
from configparser import ConfigParser

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

config = ConfigParser()
config.read('setup.cfg')

setup(
    name=config.get(section='metadata', option='name'),
    version=config.get(section='metadata', option='version'),
    description=config.get(section='metadata', option='description'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/serityops/ghmate',
    license=config.get(section='metadata', option='license'),
    license_files=config.get(section='metadata', option='license_files').split('\n'),
    packages=find_packages(),
    classifiers=config.get(section='metadata', option='classifiers').split('\n'),
    python_requires='>=3.8'
)

