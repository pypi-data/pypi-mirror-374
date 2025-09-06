from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='sconekc',
    version='0.0.5',
    find_packages=find_packages(),
    install_requires=[
        #'base64',
        'cryptography>=3.4.8',
        #'datetime',
        #'hashlib',
        #'json',
        #'os',
        #'pprint',
        'requests>=2.25.1',
        #'socket',
        #'ssl',
        #'time',
        #'zlib'
        'flask>=3.1.1'
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)
