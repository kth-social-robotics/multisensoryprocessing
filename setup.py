#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="farmi",
    install_requires=["pyzmq", "msgpack", "msgpack-numpy"],
    python_requires=">=3",
    version="3.1.2",
    description="Multisensory processing framework ",
    author="Patrik Jonell",
    author_email="pjjonell@kth.se",
    packages=find_packages(),
    scripts=["bin/farmi-server"],
)
