#!/usr/bin/python
# coding: utf8

import os

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))


TEST_REQS = [
    'pytest',
    'mock'
]


REQUIRED_PACKAGES = [
    'flask',
    'werkzeug',
    'pendulum'
]


config = {
    'description': 'Flask DataView',
    'author': 'Matthias Wutte',
    'url': '',
    "include_package_data": True,
    'download_url': 'https://github.com/wuttem',
    'author_email': 'matthias.wutte@gmail.com',
    'version': '0.2.3',
    'install_requires': REQUIRED_PACKAGES,
    'tests_require': TEST_REQS,
    'packages': find_packages(),
    'scripts': [],
    'name': 'flask-dataview'
}

setup(**config)