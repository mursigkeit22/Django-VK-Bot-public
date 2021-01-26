import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        },
    },
    'formatters': {
        'verbose': {
            'format': "[%(request_id)s] [%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': "[%(request_id)s] [%(asctime)s]  %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {

        'sends_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/send.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },

        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/django.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },

        # for the most important events; will get to code_process and info_code_process logs
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/info_code_process.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },

        'vkreceiver_file': {
            'level': 'INFO',  # what's the difference in this case? what's most sensible way?
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/vkreceiver.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },
        'request_vk_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/request_vk.log'),
            'formatter': 'simple',
            'filters': ['request_id'],

        },

        'site_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/site.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },

        'code_process_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/code_process.log'),
            'formatter': 'simple',
            'filters': ['request_id'],
        },
        'catch_all': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/catch_all.log'),
            'formatter': 'verbose',
            'filters': ['request_id'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'send': {
            'handlers': ['sends_file'],
            'propagate': False,
            'level': 'INFO',
        },
        'vkreceiver': {
            'handlers': ['vkreceiver_file'],
            'propagate': False,
            'level': 'INFO',
        },
        'code_process': {
            'handlers': ['code_process_file', 'info_file'],
            'propagate': False,

        },
        'request_vk': {
            'handlers': ['request_vk_file'],
            'propagate': False,
            'level': 'INFO',
            'encoding': 'utf8',

        },
        'site': {
            'handlers': ['site_file'],
            'propagate': False,
            'level': 'INFO',

        },
        '': {
            'handlers': ['catch_all'],
            'level': 'DEBUG',
        }
    }
}
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vk',
    'botsite',
    'authsite',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'log_request_id.middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_vk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Directories where the engine should look for template source files, in search order.
        'APP_DIRS': True,  # Whether the engine should look for template source files inside installed applications.
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

WSGI_APPLICATION = 'web_vk.wsgi.application'

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

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/login/'
