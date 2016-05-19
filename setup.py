"""
setup.py for gsTiles
"""

from distutils.core import setup 

setup(name = 'gsTiles',
      description = 'gsTiles: Python Library for making gsTiles',
      author = 'Charles R Schmidt',
      author_email = 'charlie@gwikis.com',
      url = 'https://github.com/schmidtc/gsTiles',
      version = "0.0.1",
      packages = ['gsTiles',
                  'gsTiles.npShp'],
     )
