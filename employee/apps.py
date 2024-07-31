from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import sys
from django.core.management import call_command

class EmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee'

    def ready(self):
        from .management.commands.scheduler import scheduled_task
        from .management.commands.signals import Load_Leaves
        scheduler = BackgroundScheduler(timezone='Asia/Kolkata', daemon=True)
        scheduler.add_job(scheduled_task, trigger='cron', hour=20, minute=0)
        scheduler.add_job(Load_Leaves, trigger='cron', hour=20, minute=0)
        scheduler.start()
