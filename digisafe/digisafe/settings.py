"""
Django settings for digisafe project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if IPAddr == "77.68.51.150":
    DEPLOY = True
    CURRENT_SITE = "digisafe.ircot.net"
    HTTP = "https://"
else:
    DEPLOY = False
    CURRENT_SITE = "localhost:8000"
    HTTP = "http://"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import random, string
SECRET_KEY = 'django-insecure-(j#=u5-d5y6e(fer*m04_$ib444=v11mg!uo%jocnt+k!_wxk9'
# SECRET_KEY = ''.join([random.SystemRandom().choice("{}{}{}".format(string.ascii_letters, string.digits, string.punctuation)) for i in range(50)])

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["digisafe.ircot.net", "127.0.0.1", "localhost", "192.168.10.104", "192.168.8.101", "192.168.43.249"]

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Application definition
INSTALLED_APPS = [
    'tinymce',
    'maps.apps.MapsConfig',
    'companies.apps.CompaniesConfig',
    'account.apps.AccountConfig',
    'institutions.apps.InstitutionsConfig',
    'centers.apps.CentersConfig',
    'widgets.apps.WidgetsConfig',
    'protocol.apps.ProtocolConfig',
    'courses.apps.CoursesConfig',
    'users.apps.UsersConfig',
    'countries.apps.CountriesConfig',
    'digisafe.apps.DigiSafeAdminSite', #'django.contrib.admin',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.gis",
    # 'django.contrib.sites',

    # plugin
    'leaflet',  #  maps manage
    'djgeojson',  #  maps manage
    # 'schedule',

    # SCSS compiler
    'compressor',

    'bootstrap_datepicker_plus',
]

# SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'digisafe.urls'

import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates",
                 BASE_DIR / 'templates/',
                 ],
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

WSGI_APPLICATION = 'digisafe.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
if DEPLOY:
    STATIC_ROOT = BASE_DIR / 'staticdeploy'
    STATICFILES_DIRS = [
        # STATIC_ROOT,
        BASE_DIR / 'static',
    ]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Substituting a custom User model
AUTH_USER_MODEL = 'users.User'

FILE_UPLOAD_TEMP_DIR = 'tmp'

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]

TIME_INPUT_FORMATS = [
    # '%H:%M:%S',     # '14:30:59'
    # '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
    '%H.%M',        # '14:30'
    '%H-%M',        # '14:30'
    '%H/%M',        # '14:30'
]

if DEBUG:
    EMAIL_PORT = 1025
    
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (41.8069, 12.6779),
    'DEFAULT_ZOOM': 10,
    #'MIN_ZOOM': 3,
    #'MAX_ZOOM': 18,
    'DEFAULT_PRECISION': 6,
    #'TILES': [('Satellite', 'http://server/a/...', {'attribution': '&copy; Big eye', 'maxZoom': 16}),
    #          ('Streets', 'http://server/b/...', {'attribution': '&copy; Contributors'})],
}

# Settings for deploy
SECURE_SSL_REDIRECT = False
FILE_UPLOAD_TEMP_DIR = BASE_DIR / "tmp"
if not DEBUG:
    FILE_UPLOAD_TEMP_DIR = BASE_DIR / "tmp"
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# PARAMETRI EMAIL
DEFAULT_FROM_EMAIL = "noreply@ircot.net"
if DEPLOY:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = "smtp.ionos.co.uk"
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "noreply@ircot.net"
    EMAIL_HOST_PASSWORD = "DigiSafeeMail@01012022_*"
    # EMAIL_USE_SSL = True
    EMAIL_USE_TLS = True

# SCSS compiler
STATICFILES_FINDERS = ['compressor.finders.CompressorFinder','django.contrib.staticfiles.finders.AppDirectoriesFinder']
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# settings for i18
# To create or update a message file, run this command:
# django-admin makemessages -l it
# Creating message files from JavaScript source code
# django-admin makemessages -d djangojs -l it
# To reexamine all source code and templates for new translation strings and update all message files for all locale, run this:
# django-admin makemessages -a
# The script should be run from one of two places: The root directory of your Django project or The root directory of your Django project
# django-admin compilemessages per compilare i messaggi
LOCALE_PATHS = [
    BASE_DIR / "locale/",
    # BASE_DIR / "digisafe/locale",
]
LANGUAGES = [
    ('it', _('Italian')),
    ('en', _('English')),
]

