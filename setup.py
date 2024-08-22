import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as ffile:
    README = ffile.read()

setup(
    name='django-walletpass',
    python_requires='>=3.10.0',
    version='4.1',
    author='Develatio Technologies S.L.',
    author_email='contacto@develat.io',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/develatio/django-walletpass/',
    license='BSD',
    install_requires=[
        'Django>=3.2.9',
        'cryptography>=2.4.2',
        'aioapns~=2.2',
        'pyopenssl',
        'djangorestframework>=3.8',
        'python-dateutil'
    ],
    description='Django .pkpass builder, server and push notifications',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
