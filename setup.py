#!/usr/bin/python
from setuptools import setup

setup(name='proxmoxsh',
    version='0.2',
    description='Command line utility for managing Proxmox VE',
    url='https://github.com/timur-enikeev/proxmoxsh',
    author='Timur Enikeev',
    author_email='timur-enikeev1990@ya.ru',
    license='GPLv2+',
    packages=['proxmoxsh'],
    entry_points={
    'console_scripts': [
        'proxmoxsh = proxmoxsh.__main__:main',
    ],},
      zip_safe=False)
