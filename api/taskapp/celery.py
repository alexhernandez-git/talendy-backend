from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('api')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-if-user-have-messages': {
        'task': 'check_if_user_have_messages',
        'schedule': timedelta(seconds=3),
    },
}
app.conf.timezone = 'UTC'


class CeleryAppConfig(AppConfig):
    name = 'api.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        installed_apps = [
            app_config.name for app_config in apps.get_app_configs()]

        app.autodiscover_tasks(lambda: installed_apps, force=True)
