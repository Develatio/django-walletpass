import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as ffile:
    README = ffile.read()

setup(
    name='django-walletpass',
    python_requires='>=3.5.0',
    version='2.0',
    author='Develatio Technologies S.L.',
    author_email='contacto@develat.io',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/develatio/django-walletpass/',
    license='BSD',
    install_requires=[
        'Django>=2.0',
        'cryptography>=2.4.2',
        'apns2>=0.7.1',
        'pyopenssl',
        'djangorestframework>=3.8',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
