#!/usr/bin/env python

"""
@file setup.py
@author Skylar Saveland
@date 5/21/2010
@brief Setuptools configuration for djredis
"""

version = '1.36'

sdict = {
    'name' : 'djredis',
    'version' : version,
    'description' : 'Add redis fields/methods to Django models',
    'long_description' : 'Add redis fields/methods to Django models',
    'url': 'http://github.com/skyl/djredis',
    'author' : 'Skylar Saveland',
    'author_email' : 'skylar.saveland@gmail.com',
    'maintainer' : 'Skylar Saveland',
    'maintainer_email' : 'skylar.saveland@gmail.com',
    'keywords' : ['Redis', 'key-value store', 'Django', 'Python', 'ORM', 'models'],
    'license' : 'MIT',
    'packages' : ['djredis'],
    'test_suite' : 'tests',
    'classifiers' : [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
