#!/usr/bin/env python

from setuptools import setup, find_packages

#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='Multisensory processing',
    install_requires=[
        'pyzmq',
        'msgpack',
        'msgpack-numpy'
    ],
    python_requires='>=3',
    version='2.0.0',
    description='Multisensory processing framework ',
    author='Patrik Jonell',
    author_email='pjjonell@kth.se',
    packages=find_packages(),
)
