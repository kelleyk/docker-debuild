# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='docker-debuild',
    version='0.0.1',
    description='',
    author='Kevin Kelley',
    author_email='kelleyk@kelleyk.net',
    url='https://github.com/kelleyk/docker-debuild',
    packages=find_packages(include='docker_debuild.*'),
    install_requires=[
        # 'arrow',
        'pyyaml<6.0',  # 6.0 drops support for Python 2.x
        'six',
        'intensional',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'docker-debuild = docker_debuild.build:main',
        ],
    },
)
