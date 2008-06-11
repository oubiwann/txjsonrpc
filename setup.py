import os

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

version = open('VERSION').read().strip()

def find_packages(top):
    # implement a simple find_packages so we don't have to depend on
    # setuptools
    packages = []
    for directory, subdirectories, files in os.walk(top):
        if '__init__.py' in files:
            packages.append(directory.replace(os.sep, '.'))
    return packages

setup(name="txJSON-RPC",
    version=version,
    description="Code for creating Twisted JSON-RPC servers and clients.",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://launchpad.net/txjsonrpc",
    license="MIT",
    long_description='''
        Code for creatig Twisted JSON-RPC servers and clients.
        ''',
    packages=find_packages('txjsonrpc'),
    package_dir={
        'txjsonrpc': 'txjsonrpc',
    },
    classifiers = [f.strip() for f in """
    """.splitlines() if f.strip()],

)
