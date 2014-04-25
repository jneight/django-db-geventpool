# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='django-db-geventpool',
    version='0.9',
    install_requires=[
        'gevent==1.0',
        'django>=1.5',
        'psycopg2>=2.5.1',
        'psycogreen>=1.0'],
    url='https://github.com/jneight/django-db-geventpool',
    description='Add ia DB connection pool using gevent to django',
    long_description=open("README.rst").read(),
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    author='Javier Cordero Martinez',
    author_email='jcorderomartinez@gmail.com'
)
