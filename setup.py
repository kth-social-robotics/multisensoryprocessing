#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='farmi',
    install_requires=[
        'pyzmq',
        'msgpack',
        'msgpack-numpy'
    ],
    python_requires='>=3',
    version='3.0.3',
    description='Multisensory processing framework ',
    author='Patrik Jonell',
    author_email='pjjonell@kth.se',
    packages=find_packages(),
    scripts=[
        'bin/farmi-server'
    ],
)
