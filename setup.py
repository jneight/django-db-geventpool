# coding=utf-8
import codecs

from setuptools import setup, find_packages


def long_description():
    try:
        with codecs.open('README.rst', 'r', 'utf-8') as f:
            return f.read()
    except:
        return 'Error loading README.rst'


setup(
    name='django-db-geventpool',
    version='3.2.1',
    install_requires=[
        'django>=1.11',
        'psycogreen>=1.0',
    ],
    url='https://github.com/jneight/django-db-geventpool',
    description='Add a DB connection pool using gevent to django',
    long_description=long_description(),
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    author='Javier Cordero Martinez',
    author_email='j@jcmz.me'
)
