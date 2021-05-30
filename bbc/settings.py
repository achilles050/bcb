"""
Django settings for bbc project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import smtplib

import django_heroku
import dj_database_url
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6*23oj2o%)6s650*r)xw$ofe(tqv#!oeyui=c1z$1wf+$)d-1b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost',
                 'https://kittichat.github.io/', '*']
APPEND_SLASH = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # cors
    'func',
    'member',
    'booking',
    'django.contrib.auth',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # csrf
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Disable CSRF
    'func.disable.DisableCSRF',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'func.disable.CsrfExemptSessionAuthentication',
    ],
}

ROOT_URLCONF = 'bbc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['template'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bbc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'db_bcb',
#         'HOST': '',
#         'USER': 'root',
#         'PASSWORD': '',
#         'OPTIONS': {
#             'sql_mode': 'traditional',
#         },
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'sql6414819',
#         'HOST': 'sql6.freemysqlhosting.net',
#         'USER': 'sql6414819',
#         'PASSWORD': '1f4WjUCwaS',
#         'PORT': 3306,
#         'OPTIONS': {
#             'sql_mode': 'traditional',
#         },
#     }
# }

# DATABASES = {

#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dborm4uhis5f4a',
#         'USER': 'rzpcqfieiulxgq',
#         'PASSWORD': '422352329e161dd31b60eca4c5dd88f48ccc478fb3d37cbeb95edd162c6972fc',
#         'HOST': 'ec2-3-214-136-47.compute-1.amazonaws.com',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR+'/'+'db.sqlite3',
    }
}




# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

TIME_ZONE = 'Asia/Bangkok'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# STATIC_URL = '/static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_ALLOW_ALL = False

# ALLOWED_HOSTS=['http://127.0.0.1:3000',
#                 'http://localhost:3000',
#                 'https://kittichat.github.io',
#                 '.heroku.com',]

# CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'

# CORS_ALLOWED_ORIGINS = [
#     'http://127.0.0.1:3000',
#     'http://localhost:3000',
#     'https://kittichat.github.io',
#     '.heroku.com',
# ]

# SESSION_COOKIE_DOMAIN = ['http://127.0.0.1:3000', 'http://localhost:3000', 'https://kittichat.github.io',
#                         '0.0.0.0']

# SESSION_COOKIE_DOMAIN = ['.localhost:3000', '.herokuapp.com']

# DataFlair
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "no-reply@bookingbadmintoncourt.com"
EMAIL_HOST_USER = 'bbctesting01'
EMAIL_HOST_PASSWORD = 'bbc*6263'

django_heroku.settings(locals())
