from s3.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'soccerstats_build',
        'USER': 'soccerstats',
        'PASSWORD': 'ymctas',
        'HOST': '',
        'PORT': '',
    }
}
