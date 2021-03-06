"""
setup.py for gsTiles
"""

from distutils.core import setup 

setup(name = 'gsTiles',
      version = "0.0.4",
      description = 'gsTiles: Python Library for making gsTiles',
      author = 'Charles R Schmidt',
      author_email = 'charlie@gwikis.com',
      url = 'https://github.com/schmidtc/gsTiles',
      license='MIT',
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
      ],
      keywords = 'mapping',
      #requires cairo, but it cannot be installed this way.
      # must be installed manually.
      #install_requires=['cairo', 'rtree'],
      install_requires=['rtree'],
      extras_require={'dev': ['Sphinx', 'coverage', 'nose']},
      packages = ['gsTiles',
                  'gsTiles.npShp'],
     )
