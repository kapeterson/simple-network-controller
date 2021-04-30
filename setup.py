import os
from setuptools import setup, find_packages

required = None

with open('requirements.txt') as f:
    required = f.read().splitlines()


print(required)

# Meta information
version = "1.0.0"


setup(
    # Basic info
    name='networkapp',
    version=version,
    author='krispeterson',
    author_email='kapeterson@gmail.com',
    url='',
    description='simple-vlan-controller.',
    long_description=open('README.md').read(),
    include_package_data=True,
    classifiers=[

        'Programming Language :: Python',
    ],

    # Packages and depencies
    #package_dir={'': 'networkapp'},
    packages=find_packages(),
    install_requires=required,


    # Data files
    #package_data={
    #    'python_boilerplate': [
    #    ],
    #},

    # Scripts
    entry_points={
        'console_scripts': [
            'vlan-cli=networkapp.cli.vlan_cli:main',
            'vlan-controller=networkapp.api.api:run'
        ],
    },

    platforms='any',
)
