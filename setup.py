import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-walletpass',
    version=0.1,
    author='Develatio Technologies S.L.',
    author_email='contacto@develat.io',
    packages=['django_walletpass'],
    url='http://github.com/develatio/django-walletpass/',
    license=open('LICENSE.txt').read(),
    description='Django Passbook server app',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
