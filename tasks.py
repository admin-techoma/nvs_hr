# tasks.py

from django.utils import timezone
from .employee.models import ResignApplication
import datetime
from django.db import transaction

# @shared_task
def process_resignations():
    # Get all pending resignations with a last date less than or equal to today
    pending_resignations = ResignApplication.objects.filter(
        resign_status=1, last_date__lte=timezone.now() - datetime.timedelta(minutes=2)
    )

    for resignation in pending_resignations:
        # Update the user and employee status
        resignation.employee.emp_user.is_active = False
        resignation.employee.status = 'Full&Final Pending'
        resignation.employee.save()
        resignation.employee.emp_user.save()

        # Update the resignation status to 'Approved'
        resignation.resign_status = 1
        resignation.save()

        # Schedule a new task to run on the next day
        next_day_task.apply_async((resignation.id,), eta=resignation.last_date + timezone.timedelta(days=1))


# @shared_task
def next_day_task(resignation_id):
    try:
        # Retrieve the ResignApplication object
        resignation = ResignApplication.objects.get(id=resignation_id)

        # Check if today is the day after the last_date
        if timezone.now().date() >= resignation.last_date + timezone.timedelta(days=1):
            with transaction.atomic():
                # Update the user status to False
                resignation.employee.emp_user.is_active = False
                resignation.employee.status = 'Full&Final Pending'
                resignation.employee.save()
                resignation.employee.emp_user.save()

            print("User and Employee Status Updated")
    except Exception as e:
        print(f"An error occurred: {e}")
