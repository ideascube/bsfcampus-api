#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='mook-bsf-api',
      version='1.0',
      description='The api backend for BSF mook',
      author='BSF IT team',
      author_email='it@bibliosansfrontieres.org',
      url='https://bitbucket.org/bsfcampus/mook-bsf-api',
      packages=find_packages(exclude=['tests*']),
     )
