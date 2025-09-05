from setuptools import setup, find_packages

setup(
    name='smathbyviraj',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author='Viraj',
    description='A minimal math module with sqrt, factorial, and fibonacci',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
