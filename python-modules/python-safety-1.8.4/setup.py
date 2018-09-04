#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

# there are problems to run setup.py on windows if the encoding is not set.
# additionally, supplying the encoding isn't supported on 2.7
# wrap all of this an ugly try/catch block
try:
    with open('README.md', encoding='utf8') as readme_file:
        readme = readme_file.read()
    with open('HISTORY.rst', encoding='utf8') as history_file:
        history = history_file.read()
except TypeError:
    with open('README.md') as readme_file:
        readme = readme_file.read()
    with open('HISTORY.rst') as history_file:
        history = history_file.read()

requirements = [
    'pip',
    'Click>=6.0',
    'requests',
    'packaging',
    'dparse>=0.4.1'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='safety',
    version='1.8.4',
    description="Safety checks your installed dependencies for known security vulnerabilities.",
    long_description=readme + '\n\n' + history,
    author="pyup.io",
    author_email='support@pyup.io',
    url='https://github.com/pyupio/safety',
    packages=[
        'safety',
    ],
    package_dir={'safety':
                 'safety'},
    entry_points={
        'console_scripts': [
            'safety=safety.cli:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='safety',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
