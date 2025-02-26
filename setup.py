from setuptools import setup, find_packages

setup(
    name='dns',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'networkx',
        'packaging'
    ],
    python_requires='>=3.9'
)
