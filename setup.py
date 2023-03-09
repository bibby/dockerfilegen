#!/usr/bin/env python
from distutils.core import setup

setup(
    name='dockerfilegen',
    version='1.2.5',
    description='Dockerfile generator',
    author='bibby',
    author_email='bibby@bbby.org',
    packages=['dockerfilegen'],
    install_requires=['Jinja2'],
    include_package_data=True
)
