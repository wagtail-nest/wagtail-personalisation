from setuptools import find_packages, setup


install_requires = [
    'django-polymorphic==1.0.2',
    'wagtail>=1.7',
]

tests_require = [
    'pytest==3.0.4',
    'pytest-cov==2.4.0',
    'pytest-django==3.0.0',
    'pytest-sugar==0.7.1',
    'freezegun==0.3.8',
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
