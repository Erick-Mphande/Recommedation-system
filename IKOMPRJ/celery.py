# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
# IKOMPRJ/celery.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IKOMPRJ.settings')
app = Celery('IKOMPRJ')


# Using a string here means the worker doesn’t have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))