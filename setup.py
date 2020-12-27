"""
Setup script for roles module.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from contextlib import closing
import glob

VERSION = '0.10'

with closing(open('README.txt')) as f:
    doc = f.read()


setup(
    version=VERSION,
    long_description=doc,
    platforms=["All"],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries']
    )
