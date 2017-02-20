import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

from django.urls.base import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', BASE_DIR)

MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')

MEDIA_URL = '/media/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'olj^%!kemjn61dic)!y3k!(51&vciz$2jf*w_mji-(f(nwz#7$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

from socket import gethostname
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', gethostname(), os.environ.get('OPENSHIFT_APP_DNS')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'project',
    'employee',
    'general',
    'sorl.thumbnail',
    'django_nose',
    'waffle',
    'simple_email_confirmation',
    'django_tables2',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'waffle.middleware.WaffleMiddleware',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Jiller.middleware.LoginRequiredMiddleware.LoginRequiredMiddleware',
    'Jiller.middleware.CheckProjectRelationMiddleware.CheckProjectRelation',
]

ROOT_URLCONF = 'Jiller.urls'

# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.core.context_processors.request',
# )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'Jiller.context_processors.project_list'
            ],
        },
    },
]

WSGI_APPLICATION = 'Jiller.wsgi.application'

LOGIN_REDIRECT_URL = reverse_lazy('general:home_page')
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join('../static')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


AUTH_USER_MODEL = 'employee.Employee'

LOGIN_URL = 'general:login'

LOGIN_EXEMPT_URLS = (
 r'^login/$',
 r'^registration/$',
 r'^confirmation/(?P<username>[a-zA-Z0-9]+)/(?P<key>[a-zA-Z0-9]+)/$',
 r'^sender/(?P<username>[a-zA-Z0-9]+)/$',
 r'^accounts/github/login/$',
)


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=general,project,employee',
]

PAGINATION_PER_PAGE = 20

try:
    from .local_settings import *
except ImportError:
    pass

# CELERY
BROKER_URL = 'redis://localhost:6379'
# CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ['general.tasks']
CELERY_TIMEZONE = 'UTC'


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'email.assign.python.webui@gmail.com'
EMAIL_HOST_PASSWORD = 'Evrey123'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'email.assign.python.webui@gmail.com'

