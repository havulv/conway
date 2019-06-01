#! /usr/bin/env python3.6

from setuptools.command.install import Install
from setuptools import setup, find_packages

import subprocess as sbp


class MakeLife(Install):
    def run(self):
        sbp.run(["make"])
        Install.run(self)


setup(name='conway',
      version='1.0.0',
      packages=find_packages(exclude=['*.tests', '*.tests.*',
                                      'tests.*', 'tests']),
      package_dir={'conway': 'conway'},
      url='https://github.com/jandersen7/conway',
      author="John Andersen",
      author_email="johnandersen185@gmail.com",
      description="Some fun with conway's game of life! Try out some celullar automata.",
      install_requires=[],
      cmdclass={'install': MakeLife})
