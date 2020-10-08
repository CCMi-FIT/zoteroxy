from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = ''.join(f.readlines())

setup(
    name='zoteroxy',
    version=0.1,
    keywords='zotero proxy api',
    description='Proxy service providing data from Zotero in a convenient way',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'aiohttp-jinja2',
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
