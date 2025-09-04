# setup.py
from setuptools import setup, find_packages

setup(
    name='aim2numpy',
    version='0.3.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    author='Alejandro Gutierrez',
    author_email='alejandro.gutierrez@ucalgary.ca',
    description='A library to convert Scanco AIM image files to numpy arrays and extract header information',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Alexhal9000/aim2numpy', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
