from web_vk.settings.base_settings import *

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', os.environ['HOST'], os.environ['HOST1'], os.environ['HOST2'], ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '',
    }
}

CELERY_BROKER_URL = 'amqp://localhost'

CELERYD_PREFETCH_MULTIPLIER = 1

CELERY_BEAT_SCHEDULE = {

    "newpost_task": {
        "task": "vk.tasks.newpost_periodic",
        "schedule": 60.0,
        "options": {"priority": 9, }

    },
}
