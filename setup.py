#!/usr/bin/env python3
#
# DEWI: a developer tool and framework
# Copyright (C) 2012-2022  Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

if sys.hexversion < 0x030a0000:
    raise RuntimeError("Required python version: 3.10 or newer (current: %s)" % sys.version)

from setuptools import setup, find_packages

setup(
    name="dewi_commands",
    description="A toolchain and framework for everyday tasks",
    license="LGPLv3",
    version="3.1.0",
    author="Laszlo Attila Toth",
    author_email="python-dewi@laszloattilatoth.me",
    maintainer="Laszlo Attila Toth",
    maintainer_email="python-dewi@laszloattilatoth.me",
    keywords='tool framework development synchronization',
    url="https://github.com/LA-Toth/dewi_commands",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    zip_safe=True,
    use_2to3=False,
    python_requires='>=3.10',
    packages=find_packages(exclude=['pylintcheckers', '*test*']),
    install_requires=[
        'dewi_core >=5.0.0, <6',
        'dewi_module_framework>=2.0.1',
        'dewi_logparsers >=2.0.2, <3',
        'dewi_utils >=3.0.0, <4',
        'dewi_realtime_sync >=2.0.0, <3',
        'lxml',
        'selenium',
        'sqlalchemy',
        'pyyaml',
        'urllib3 <2',
    ]
)
