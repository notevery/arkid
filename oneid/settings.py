"""
Django settings for oneid project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import datetime

from kombu import Exchange, Queue

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pueg+1f_su-h_=wxz98+gr9#f5_49f-267^%j^ry^pbcd4+wio'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TESTING = False    # always False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_celery_results',
    'django_celery_beat',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_expiring_authtoken',
    'coreapi',
    'tasksapp',
    'siteadmin',
    'siteapi',
    'oneid_meta',
    'oauth2_provider',
    'infrastructure',
    'captcha',
    # 'ldap.sql_backend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oneid.authentication.CustomExpiringTokenAuthentication',
        'oneid.authentication.HeaderArkerBaseAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'oneid.permissions.IsAdminUser',
    )
}

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',    # 保留，用于登录django admin。注意：两个体系中账号密码一样会返回django_user
    'oneid.auth_backend.OneIDBasicAuthBackend',
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.django.middleware.CrequestMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SITE_ID = 1
SITE_META = 'native'

ROOT_URLCONF = 'oneid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'infrastructure', 'templates')],
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

# log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

WSGI_APPLICATION = 'oneid.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True    # pylint: disable=invalid-name

USE_TZ = True

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ('*', )
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
)

EXECUTERS = [    # 注意顺序
    'executer.RDB.RDBExecuter',
    'executer.log.rdb.RDBLogExecuter',
    'executer.cache.default.CacheExecuter',
    # 'executer.LDAP.LDAPExecuter',
    # 'executer.Ding.DingExecuter',
]

EXECUTER_WIP = False

# LDAP

LDAP_SERVER = 'ldap://localhost'
LDAPS_SERVER = 'ldaps://localhost'
LDAP_BASE = 'dc=example,dc=org'
LDAP_USER = 'cn=admin,{}'.format(LDAP_BASE)
LDAP_USER_BASE = 'ou=people,{}'.format(LDAP_BASE)
LDAP_DEPT_BASE = 'ou=dept,{}'.format(LDAP_BASE)
LDAP_GROUP_BASE = 'cn=intra,ou=group,{}'.format(LDAP_BASE)
LDAP_PASSWORD = 'admin'

# PASSWORD
# one of 'MD5', 'SMD5', 'SHA', 'SSHA'
PASSWORD_ENCRYPTION = 'SMD5'

# Redis
REDIS_CONFIG = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": 60 * 60 * 24 * 3,
        "OPTIONS": {
            "MAX_ENTRIES": None,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# CELERY
CELERY_BROKER_URL = 'redis://{}:{}/{}'.format(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB'])
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
from celery_app import app    # pylint: disable=wrong-import-position,unused-import
CELERY_TASK_QUEUES = [
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('perm', Exchange('perm'), routing_key='perm'),
    Queue('dept', Exchange('dept'), routing_key='dept'),
    Queue('group', Exchange('group'), routing_key='group'),
]
CELERY_TASK_DEFAULT_QUEUE = 'default'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'upload')
DOWNLOAD_URL = STATIC_URL + 'download'

REDIS_HOST = 'localhost'

DOMAIN = ''
PRIVATE_IP = '127.0.0.1'
PUBLIC_IP = ''
BASE_URL = 'http://localhost'

FE_TOKEN_URL = '/oauth/fe/token/'
# TODO
FE_EMAIL_REGISTER_URL = '/oneid#/oneid/signup'    # 邮件注册页面
FE_EMAIL_RESET_PWD_URL = '/oneid#/oneid/password'    # 邮件重置密码页面
FE_EMAIL_ACTIVATE_USER_URL = '/oneid#/oneid/activate'    # 邮件激活账号页面
FE_EMAIL_UPDATE_EMAIL_URL = '/oneid/#/reset_email_callback'    # 邮件重置邮箱页面
LOGIN_URL = '/_/#/oneid/login'
LOGIN_URL = '/#/oneid/login'

CREDIBLE_ARKERS = [
    'oneid_broker',
    'arkbe_broker',
    'wfe',
    'msghub',
    'oauth',
]

# Minio
MINIO_ENDPOINT = 'localhost:9000'
MINIO_ACCESS_KEY = ''
MINIO_SECRET_KEY = ''
MINIO_SECURE = True
MINIO_LOCATION = 'us-east-1'

MINIO_BUCKET = 'oneid'

# 钉钉
DINGDING_APP_KEY = ''
DINGDING_APP_SECRET = ''
DINGDING_APP_VERSION = 1
AGENT_ID = 0

# SMS
SMS_LIFESPAN = datetime.timedelta(seconds=120)
SMS_ALIYUN_REGION = 'cn-hangzhou'
SMS_ALIYUN_PRODUCT_NAME = 'Dysmsapi'
SMS_ALIYUN_DOMAIN = 'dysmsapi.aliyuncs.com'
SMS_ALIYUN_ACCESS_KEY_ID = ''
SMS_ALIYUN_ACCESS_KEY_SECRET = ''
SMS_ALIYUN_TEMPLATE_CODE = ''
SMS_ALIYUN_SIGNATURE = ''

ACTIVE_USER_DATA_LIFEDAY = 30
ACTIVE_USER_REDIS_KEY_PREFIX = 'active-'

if os.path.exists(os.path.join(BASE_DIR, 'falcon', 'settings_domain.py')):
    exec(open(os.path.join(BASE_DIR, 'falcon', 'settings_domain.py')).read())

if os.path.exists(os.path.join(BASE_DIR, 'falcon', 'settings_celery.py')):
    exec(open(os.path.join(BASE_DIR, 'falcon', 'settings_celery.py')).read())

if os.path.exists(os.path.join(BASE_DIR, 'settings_local.py')):
    exec(open(os.path.join(BASE_DIR, 'settings_local.py')).read())
