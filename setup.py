import os
from setuptools import setup, find_packages
from distutils.command.upload import upload
from distutils.command.register import register
from configparser import ConfigParser



class Register(register):

    @staticmethod
    def _get_rc_file():
        return os.path.join('.', '.pypirc')


class Upload(upload):

    @staticmethod
    def _get_rc_file():
        return os.path.join('.', '.pypirc')


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
    license_file=config.get('metadata', 'license_file').split('\n'),
    packages=find_packages(),
    classifiers=config.get('metadata', 'classifiers').split('\n'),
    python_requires='>=3.8',
    cmdclass={
        'register': Register,
        'upload': Upload,
    }
)


