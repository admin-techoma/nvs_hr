# hr/apps.py

from django.apps import AppConfig

class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'

    def ready(self):
        # Import the `scheduled_task` function here to initialize the scheduler
        from .models import scheduled_task
