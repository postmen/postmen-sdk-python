from setuptools import setup
from codecs import open  # To use a consistent encoding
from os import path
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='postmen',

    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='1.0',

    description='Python SDK of Postmen API',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/postmen/sdk-python',

    # Download path
    download_url = 'https://github.com/postmen/sdk-python/tarball/1.0',

    # Author details
    author='Postmen',
    author_email='support@postmen.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='postmen api binding post mail airmail logistics shipping label rate rates',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['postmen'],
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'requests==2.7.0',
        'python-dateutil==2.4.2',
        'six==1.9.0',
        'responses==0.5.1'
    ],
    tests_require=[
        'pytest'
    ]
)
