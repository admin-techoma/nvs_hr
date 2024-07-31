# hr/management/commands/run_scheduled_task.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management.base import BaseCommand
from django.utils import timezone
from hr.models import scheduled_task

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run scheduled tasks'

    def handle(self, *args, **options):
        try:
            timezone.activate(timezone.get_current_timezone())
            scheduler = BackgroundScheduler(timezone='Asia/Kolkata', daemon=True)
            scheduler.add_job(scheduled_task, trigger='cron', hour=22, minute=43)
            scheduler.start()

            
        except Exception as e:
            logger.error("Error in scheduled task: {}".format(e))
