#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here,'README.md')) as readme_file:
    readme = readme_file.read()


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
    'description': "Flask Data Visualization Helpers",
    'long_description': readme,
    'long_description_content_type': "text/markdown",
    'url': 'https://github.com/wuttem/flask-dataview',
    "include_package_data": True,
    'download_url': 'https://github.com/wuttem',
    'author_email': 'matthias.wutte@gmail.com',
    'version': '0.3.0',
    'install_requires': REQUIRED_PACKAGES,
    'tests_require': TEST_REQS,
    'packages': find_packages(),
    'scripts': [],
    'name': 'flask-dataview'
}

setup(**config)