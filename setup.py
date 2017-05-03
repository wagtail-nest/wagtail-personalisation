from setuptools import find_packages, setup


install_requires = [
    'wagtail<=1.10',
    'user-agents>=1.0.1',
]

tests_require = [
    'pytest==3.0.4',
    'pytest-cov==2.4.0',
    'pytest-django==3.0.0',
    'pytest-sugar==0.7.1',
    'freezegun==0.3.8',
    'factory_boy==2.8.1',
    'wagtail_factories==0.2.0',
]

docs_require = [
    'sphinx>=1.4.0',
]

setup(
    name='wagtail-personalisation',
    version='0.1.0',
    description='A Wagtail add-on for showing personalized content',
    author='Lab Digital BV',
    author_email='b.besemer@labdigital.nl',
    url='http://labdigital.nl',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'docs': docs_require,
        'test': tests_require,
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
