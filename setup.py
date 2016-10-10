# -*- coding: utf-8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/python-boilerplate/
#

import os
import sys
import codecs
import warnings

from setuptools import setup, find_packages
from setuptools.command.install import install as _install


# Save version and author to __meta__.py
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'src', 'boxed', '__meta__.py')
meta = '''# Automatically created. Please do not edit.
__version__ = u'%s'
__author__ = u'F\\xe1bio Mac\\xeado Mendes'
''' % version
with open(path, 'w') as F:
    F.write(meta)

    
# Adapt the install command to execute setcap in the end of installation
class install(_install):
    def run(self):
        super(install, self).run()

        if os.getuid() == 0:
            py_path = os.path.realpath(sys.executable)
            boxed_path = '/usr/bin/python_boxed'
            with open(py_path, 'rb') as src:
                with open(boxed_path, 'wb') as dest:
                    dest.write(src.read())
            os.system('setcap cap_setuid+ep %s' % boxed_path)
            os.system('chmod +x %s' % boxed_path)
        else:
            warnings.warn(
                'not superuser: you must configure the python_boxed '
                'executable manually. Please make a copy of the python'
                'interpreter and run the command `setcap cap_setuid+ep '
                '<file>` on it.'
            )
            
# Boxed only works on linux
if not sys.platform.startswith('linux'):
    warnings.warn(
        'you are using %s. Boxed only works on linux!' % sys.platform,
        RuntimeWarning,
    )


setup(
    # Basic info
    name='boxed',
    version=version,
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='http://github.com/fabiommendes/boxed/',
    description='Simple and lightweight sandbox solution for Python an Linux.',
    long_description=codecs.open('README.rst', 'rb', 'utf8').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'pexpect>=4.2',
        'psutil>=4.3',
    ],
    extras_require={
        'dev': [
            'python-boilerplate',
            'invoke>=0.13',
            'pytest',
            'pytest-cov',
            'manuel',
        ],
        'cloudpickle': ['cloudpickle'],
        'dill': ['dill'],
    },

    # Script
    entry_points={
        'console_scripts': [
            'boxed = boxed.__main__:main',
        ]
    },

    # Other configurations
    zip_safe=False,
    platforms='linux',
    cmdclass={'install': install},
)
