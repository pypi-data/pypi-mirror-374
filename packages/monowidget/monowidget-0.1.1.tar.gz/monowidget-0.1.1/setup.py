#!/usr/bin/env python
# coding:utf-8
import os
import sys
from setuptools import find_packages, setup

setup(
    name='monowidget',
    version='0.1.1',
    description='A modern PyQt6 parameter interface library for creating interactive configuration panels with automatic UI generation.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="Eagle'sBaby",
    author_email='2229066748@qq.com',
    maintainer="Eagle'sBaby",
    maintainer_email='2229066748@qq.com',
    url='https://github.com/monowidget/monowidget',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Desktop Environment',
        'Topic :: Software Development :: User Interfaces',
    ],
    keywords=['pyqt6', 'parameter', 'interface', 'configuration', 'ui', 'widget', 'inspector'],
    python_requires='>=3.10',
    install_requires=[
        "PyQt6",
        "rbpop>=0.3",
    ],
)
