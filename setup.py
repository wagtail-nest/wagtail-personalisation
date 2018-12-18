import re
from setuptools import find_packages, setup

install_requires = [
    'wagtail>=2.0,<2.1',
    'user-agents>=1.0.1',
    'wagtailfontawesome>=1.1.3',
]

tests_require = [
    'factory_boy==2.8.1',
    'flake8',
    'flake8-blind-except',
    'flake8-debugger',
    'flake8-imports',
    'freezegun==0.3.8',
    'pytest-cov==2.4.0',
    'pytest-django==3.1.2',
    'pytest-sugar==0.7.1',
    'pytest-mock==1.6.3',
    'pytest==3.1.0',
    'wagtail_factories==1.1.0',
]

docs_require = [
    'sphinx>=1.4.0',
]

with open('README.rst') as fh:
    long_description = re.sub(
        '^.. start-no-pypi.*^.. end-no-pypi', '', fh.read(), flags=re.M | re.S)

setup(
    name='wagtail-personalisation-molo',
    version='1.0.0',
    description='A forked version of Wagtail add-on for showing personalized content',
    author='Praekelt.org',
    author_email='dev@praekeltfoundation.org',
    url='https://github.com/praekeltfoundation/wagtail-personalisation/',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'docs': docs_require,
        'test': tests_require,
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MIT',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
