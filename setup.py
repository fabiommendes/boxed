# -*- coding: utf8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/boilerplate/
#

import os
import sys
import warnings
from setuptools import setup, find_packages


# It only works on linux
if sys.platform != 'linux':
    raise SystemExit('you are using %s. Boxed only works on linux!' %
                     sys.platform)

# Meta information
name = 'boxed'
author = 'Fábio Macêdo Mendes'
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)

# Save version and author to __meta__.py
with open(os.path.join(dirname, 'src', name, '__meta__.py'), 'w') as F:
    F.write('__version__ = %r\n__author__ = %r\n' % (version, author))


setup(
    # Basic info
    name=name,
    version=version,
    author=author,
    author_email='fabiomacedomendes@gmail.com',
    url='',
    description='Simple and lightweight sandbox solution for Python an Linux.',
    long_description=open('README.rst').read(),

    # Classifiers (see http://...)
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and depencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[],
    extras_require={
        'testing': ['pytest'],
        'cloudpickle': ['cloudpickle'],
        'dill': ['dill'],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
    test_suite='%s.test.test_%s' % (name, name),
)

if 'install' in sys.argv:
    if os.getuid() == 0:
        py_path = os.path.realpath(sys.executable)
        boxed_path = '/usr/bin/python_boxed'
        with open(py_path, 'rb') as src:
            with open(boxed_path, 'wb') as dest:
                dest.write(src.read())
        os.system('setcap cap_setuid+ep %s' % boxed_path)
        os.system('chmod +x %s' % boxed_path)
    else:
        warnings.warn('not superuser: you must configure the python_boxed '
                      'executable manually. Please make a copy of the python'
                      'interpreter and run the command `setcap cap_setuid+ep '
                      '<file>` on it.')