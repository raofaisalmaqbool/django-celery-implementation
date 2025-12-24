"""
Django Settings for Celery Test Project
========================================
Comprehensive Django settings with environment variable support.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-)==9#zpkp=#0-tke^_pn$9+#yb===!npd@l@*%!cx7zswbdppj')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django_celery_results',  # Store Celery task results in Django DB
    'django_celery_beat',     # Periodic task scheduler
    
    # Local apps
    'app',
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

ROOT_URLCONF = 'celerytest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'celerytest.wsgi.application'


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True


# ============================================================================
# STATIC AND MEDIA FILES
# ============================================================================
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config('REDIS_CACHE_URL', default='redis://127.0.0.1:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# ============================================================================
# CELERY CONFIGURATION
# ============================================================================
# Celery broker and result backend
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND',
    default='django-db'  # Store results in Django database
)

# Celery task settings
CELERY_TASK_TRACK_STARTED = True  # Track when tasks start
CELERY_TASK_TIME_LIMIT = config('CELERY_TASK_TIME_LIMIT', default=30 * 60, cast=int)  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = config('CELERY_TASK_SOFT_TIME_LIMIT', default=25 * 60, cast=int)  # 25 minutes
CELERY_TASK_SEND_SENT_EVENT = True  # Send task-sent events
CELERY_TASK_IGNORE_RESULT = False  # Don't ignore task results

# Celery serialization settings
CELERY_ACCEPT_CONTENT = ['json']  # Accept only JSON
CELERY_TASK_SERIALIZER = 'json'   # Serialize tasks as JSON
CELERY_RESULT_SERIALIZER = 'json' # Serialize results as JSON

# Celery timezone and schedule settings
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='UTC')
CELERY_ENABLE_UTC = True

# Celery cache backend
CELERY_CACHE_BACKEND = 'django-cache'

# Celery result backend settings
CELERY_RESULT_EXTENDED = True  # Store additional metadata
CELERY_RESULT_EXPIRES = config('CELERY_RESULT_EXPIRES', default=3600, cast=int)  # 1 hour

# Worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = config('CELERY_WORKER_PREFETCH_MULTIPLIER', default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config('CELERY_WORKER_MAX_TASKS_PER_CHILD', default=1000, cast=int)

# Beat schedule for periodic tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Example: Clean up old task logs every day at midnight
    'cleanup-task-logs': {
        'task': 'app.tasks.cleanup_task_logs',
        'schedule': crontab(hour=0, minute=0),
        'args': (7,),  # Delete logs older than 7 days
    },
    # Example: Health check every 5 minutes
    'health-check': {
        'task': 'app.tasks.health_check',
        'schedule': crontab(minute='*/5'),
    },
}

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'  # Print emails to console in development
)
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@celerytest.com')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'celery.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console', 'file'],
            'level': config('CELERY_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'app.tasks': {
            'handlers': ['console', 'file'],
            'level': config('APP_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}