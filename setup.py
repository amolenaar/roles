"""
Setup script for roles module.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from contextlib import closing


VERSION = '0.5.0'

with closing(open('README.rst')) as f:
    doc = f.read()


setup(
    name='roles',
    version=VERSION,
    description='Role based development',
    long_description=doc,
    author='Arjan Molenaar',
    author_email='gaphor@gmail.com',
    url='http://github.org/amolenaar/roles',
    license="BSD License",
    py_modules = ['roles'],
    keywords="role DCI",
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
