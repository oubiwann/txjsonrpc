import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

setup(name="Twisted-JSONRPC",
    version=version,
    description="Python Enterprise Monitoring Application",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://projects.adytum.us/tracs/JSON-RPC",
    license="BSD",
    long_description='''pymon is an open source network and process
        monitoring solution implemented in python. The interface and
        conifiguration is designed to be easily and rapidly deployed,
        saving on time and overhead often associated with other 
        monitoring solutions.''',
    packages=[
        'pymon',
        'pymon.twisted',
        'pymon.twisted.protocols',
        'pymon.twisted.web',
        'pymon.twisted.web2',
    ],
    package_dir = {
        'adytum': 'adytum',
    },
    zip_safe=False,
    classifiers = [f.strip() for f in """
    """.splitlines() if f.strip()],

)
