# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create a Celery instance and configure it using the settings from Django.
celery = Celery('core')

# Load task modules from all registered Django app configs.
celery.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps.
celery.autodiscover_tasks()

# Set broker_connection_retry_on_startup to True
celery.conf.broker_connection_retry_on_startup = True

if __name__ == '__main__':
    celery.start()
