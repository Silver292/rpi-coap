#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('readme.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'CoAPthon3==1.0.1'
] + ['Adafruit-DHT==1.4.0'] if sys.platform.startswith("linux") else []

setup(
    name='rpicoap',
    version='0.1.0',
    description="Python program to read temperature and humidity data from \
    a DHT22 sensor and send it to a ThingsBoard dashboard.",
    long_description=readme,
    author="Tom Scott",
    author_email='tomscott292@gmail.com',
    url='https://github.com/silver292/rpi-coap',
    entry_points = {
        'console_scripts' : ['rpicoap = rpicoap.rpicoap:main']
    },
    packages=[
        'rpicoap',
    ],
    package_dir={'rpicoap':
                 'rpicoap'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='rpicoap',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
)
