import os
import re
import sys
from setuptools import setup, find_packages

version_file = os.path.join(
    os.path.dirname(__file__),
    'flask_slimrest',
    '__version__.py'
)


with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.MULTILINE
    )
    version = m.groups(1)[0]


requirements = [
    'flask>=0.10',
    'marshmallow>=2.0.0'
]


setup(
    name='Flask-SlimREST',
    version=version,
    license='MIT',
    url='https://github.com/fabian-rump/flask-slimrest/',
    author='Fabian Rump',
    author_email='fabian@cgro.net',
    description='Flask extension for building RESTful APIs',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    platforms='any',
    test_suite = 'nose.collector',
    install_requires=requirements,
    tests_require=['nose', 'coverage'],
)