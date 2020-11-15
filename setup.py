from setuptools import setup, find_packages
import os

from zoteroxy.consts import APPNAME, VERSION, DESCRIPTION

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = ''.join(f.readlines())

setup(
    name=APPNAME.lower(),
    version=VERSION,
    keywords='zotero proxy api',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CCMi-FIT/zoteroxy',
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.6, <4',
    install_requires=[
        'aiohttp',
        'aiohttp_cors',
        'aiohttp-jinja2',
        'aiohttp-swagger',
        'pyhumps',
        'Pyzotero',
        'PyYAML',
    ],
    classifiers=[
        'Framework :: AsyncIO',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],
)
