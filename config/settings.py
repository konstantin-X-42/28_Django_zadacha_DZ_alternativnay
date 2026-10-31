import os
from pathlib import Path
import ssl

from django.conf.global_settings import STATICFILES_DIRS

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6wn$4t7@nzof9-j*9vnkkq5@%=sg#pm2ouvzk7ua+l$^s=g+$j'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dogs',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "23_Django_zadacha_DZ_alternativnay",
        'USER': 'kosty',
        'PASSWORD': '16011984',
        'HOST': '127.0.0.1',
        'PORT': 5433,
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATICFILES_DIRS = (BASE_DIR / 'static/',)

# MAILERS = {
#     'default': {
#         'BACKEND': 'django.core.mail.backends.console.EmailBackend',
#     },
# }

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# при авторизации будет применена эта модель
AUTH_USER_MODEL = 'users.User'

# перенаправляем на главную страницу
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'

EMAIL_HOST_USER = "kostyani4@mail.ru"
EMAIL_HOST_PASSWORD = "2vU3g700JegQ2tjE9DK4"
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Отключаем строгую верификацию SSL-сертификатов для отправки почты
ssl._create_default_https_context = ssl._create_unverified_context

# исключает ошибку при нажатии кнопки ВЫХОД пользователя
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
