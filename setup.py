#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'boto3>=1.5.0', 'awscli>=1.13.0']

setup_requirements = [ 'sphinx', 'twine', 'bumpversion' ]

test_requirements = [ 'flake8', 'tests', 'tox' ]

setup(
    author="Aidan Melen",
    author_email='aidan.l.melen@gmail.com',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
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
        'Programming Language :: Python :: 3.7',
    ],
    description="awscli_bastion extends the awscli by managing mfa protected short-lived credentials.",
    entry_points={
        'console_scripts': [
            'bastion=awscli_bastion.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='awscli_bastion',
    name='awscli_bastion',
    packages=find_packages(include=['awscli_bastion']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/aidanmelen/awscli_bastion',
    version='0.2.0',
    zip_safe=False,
)
