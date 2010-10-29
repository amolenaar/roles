"""
Setup script for roles module.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from contextlib import closing
import glob

VERSION = '0.8'

with closing(open('README.txt')) as f:
    doc = f.read()


setup(
    name='roles',
    version=VERSION,
    description='Role based development',
    long_description=doc,
    author='Arjan Molenaar',
    author_email='gaphor@gmail.com',
    url='http://github.com/amolenaar/roles',
    license="BSD License",
    packages = [ 'roles' ],
    keywords="role DCI data context interaction",
    platforms=["All"],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'],
    zip_safe=False
    )

#vim:sw=4:et:ai
