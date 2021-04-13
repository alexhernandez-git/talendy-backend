"""Task app."""

# Django
from django.apps import AppConfig


class TasksAppConfig(AppConfig):
    """Task app config."""
    name = 'api.tasks'
    verbose_name = 'Tasks'
