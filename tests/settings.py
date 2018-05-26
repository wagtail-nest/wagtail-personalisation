from __future__ import absolute_import, unicode_literals

import os
from pkg_resources import parse_version as V

import django


DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', 'db.sqlite3'),
    }
}

ALLOWED_HOSTS = ['localhost']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SECRET_KEY = 'not needed'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ROOT_URLCONF = 'tests.site.urls'

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

USE_TZ = False

TESTS_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(TESTS_ROOT, 'site', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'debug': True,
        },
    },
]


def get_middleware_settings():
    return (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        'wagtail.wagtailcore.middleware.SiteMiddleware',
    )


# Django 1.10 started to use "MIDDLEWARE" instead of "MIDDLEWARE_CLASSES".
if V(django.get_version()) < V('1.10'):
    MIDDLEWARE_CLASSES = get_middleware_settings()
else:
    MIDDLEWARE = get_middleware_settings()

INSTALLED_APPS = (
    'wagtail_personalisation',

    'wagtail.contrib.modeladmin',
    'wagtail.wagtailsearch',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailimages',
    'wagtail.wagtaildocs',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',

    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tests.site.pages',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # don't use the intentionally slow default password hasher
)

WAGTAIL_SITE_NAME = 'wagtail-personalisation test'
