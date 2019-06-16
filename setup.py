#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="farmi",
    install_requires=["pyzmq", "msgpack", "msgpack-numpy", "lz4"],
    python_requires=">=3",
    version="3.1.4",
    description="Multisensory processing framework ",
    author="Patrik Jonell",
    author_email="pjjonell@kth.se",
    packages=find_packages(),
    scripts=["bin/farmi-server"],
)
