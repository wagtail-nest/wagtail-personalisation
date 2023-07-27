import re

from setuptools import find_packages, setup

install_requires = [
    "wagtail>=4.1",
    "user-agents>=1.1.0",
    "wagtailfontawesome>=1.2.1",
    "pycountry",
]

tests_require = [
    "factory_boy==3.2.1",
    "flake8-blind-except",
    "flake8-debugger",
    "flake8-isort",
    "flake8",
    "freezegun==1.2.1",
    "pytest-cov==3.0.0",
    "pytest-django==4.5.2",
    "pytest-pythonpath==0.7.4",
    "pytest-sugar==0.9.4",
    "pytest==6.2.5",
    "wagtail_factories==4.0.0",
    "pytest-mock==3.8.1",
]

docs_require = [
    "sphinx>=1.7.6",
    "sphinx_rtd_theme>=0.4.0",
]

with open("README.rst") as fh:
    long_description = re.sub(
        "^.. start-no-pypi.*^.. end-no-pypi", "", fh.read(), flags=re.M | re.S
    )

setup(
    name="wagtail-personalisation",
    version="0.15.3",
    description="A Wagtail add-on for showing personalized content",
    author="Lab Digital BV and others",
    author_email="opensource@labdigital.nl",
    url="https://labdigital.nl/",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "docs": docs_require,
        "test": tests_require,
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="MIT",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 4",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],
)
