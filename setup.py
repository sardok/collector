from setuptools import setup, find_packages

setup(
    name='collector',
    version='0.1',
    description='An ORM for Scrapinghub Collections.',
    packages=find_packages(),
    py_modules=['collector'],
    test_suite='tests'
)
