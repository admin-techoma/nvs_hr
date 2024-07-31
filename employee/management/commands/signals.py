import logging
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone
from datetime import date
from employee.models import Employee, LeaveBalance

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load leave balances for new employees'

    def handle(self, *args, **options):
        try:
            timezone.activate(timezone.get_current_timezone())
            Load_Leaves()
        except Exception as e:
            logger.error("Error in scheduled task: {}".format(e))


def Load_Leaves():
    try:
        timezone.activate(timezone.get_current_timezone())
        # logger.info("=============LOGGER CHECK")
        today = timezone.now().date()  # Get the current date in the local timezone

        # Check if today's date is less than the 12th day of the month
        if today.day < 12:
            total_leaves = 2
        else:
            total_leaves = 1

        # Filter employees whose Date of Joining matches today's date
        new_employees = Employee.objects.all() #filter(doj=today)
        for employee in new_employees:
            # Check if the employee already has a leave balance record
            existing_balance = LeaveBalance.objects.filter(employee=employee).exists()

            if not existing_balance:
                # Create a new leave balance record for the employee
                LeaveBalance.objects.create(employee=employee, total_leaves=total_leaves)

        # Increment leave balance by 2 on the 1st day of each month
        if today.day == 1:
            LeaveBalance.objects.all().update(total_leaves=F('total_leaves') + 2)

        # Check if it's March and adjust total_leaves accordingly
        if today.month == 3:
            # Get employees whose leave balance needs adjustment
            employees_to_adjust = LeaveBalance.objects.filter(total_leaves__gt=10)
            for employee in employees_to_adjust:
                employee.total_leaves = 10
                employee.save()

    except Exception as e:
        logger.error("Error loading leave balances: {}".format(e))

