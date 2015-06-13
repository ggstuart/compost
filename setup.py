#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='compost',
    version='0.1',
    description='Compost is an energy consumption modelling toolkit for inverse modelling of energy consumption using measured data',
    author='Graeme Stuart',
    author_email='gstuart@dmu.ac.uk',
    url='https://github.com/compost',
    requires=[
        'pandas'
    ],
    packages=find_packages(),
)
