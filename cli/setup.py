"""
Setup configuration for B1 LMS CLI

Install with: pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name='b1-lms-cli',
    version='0.1.0',
    description='Command-line interface for B1 Learning Management System',
    author='B1 LMS Team',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'rich>=13.7.0',
        'click>=8.1.0',
    ],
    entry_points={
        'console_scripts': [
            'lms=lms_cli.cli:cli',
        ],
    },
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.14',
    ],
)
