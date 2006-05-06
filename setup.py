import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

setup(name="Twisted-JSONRPC",
    version=version,
    description="Twisted JSON-RPC servers and clients.",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://projects.adytum.us/tracs/JSON-RPC",
    license="BSD",
    long_description='''
        Twisted JSON-RPC servers and clients.
        ''',
    packages=[
        'adytum',
        'adytum.twisted',
        'adytum.twisted.protocols',
        'adytum.twisted.web',
        'adytum.twisted.web2',
    ],
    package_dir = {
        'adytum': 'adytum',
    },
    zip_safe=False,
    classifiers = [f.strip() for f in """
    """.splitlines() if f.strip()],

)
