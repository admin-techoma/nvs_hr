import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management.base import BaseCommand
from django.utils import timezone
from employee.models import Employee, Attendance, LeaveApplication
from datetime import datetime, time, timedelta, date
import pytz
from django.db.models import Q

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run scheduled tasks'

    def handle(self, *args, **options):
        try:
            timezone.activate(timezone.get_current_timezone())
            scheduled_task()
        except Exception as e:
            logger.error("Error in scheduled task: {}".format(e))
            
def scheduled_task():
    try:
        # Set the timezone explicitly at the beginning of the task
        timezone.activate(timezone.get_current_timezone())
        # logger.info("Scheduled task started at {}".format(timezone.now()))

        current_date = timezone.now().date()
        if current_date.weekday() in [6]:  #Sunday = 6
        # It's a weekend, skip marking attendance
            pass
        else:
            current_time = timezone.now().time()

            start_of_day = datetime.strptime("09:00", "%H:%M").time()
            end_of_day = datetime.strptime("18:00", "%H:%M").time()

            # Check attendance for each employee
            employees = Employee.objects.all()
            LEAVE_STATUS_APPROVED = 1

            for employee in employees:
                attendance_exists = Attendance.objects.filter(
                    employee=employee,
                    date=current_date
                ).exists()

                leave_exists = LeaveApplication.objects.filter(
                    employee=employee,
                    leave_from_date__lte=current_date,
                    leave_to_date__gte=current_date,
                    leave_status=LEAVE_STATUS_APPROVED
                ).exists()

                if not attendance_exists and not leave_exists:
                    Attendance.objects.create(
                        employee=employee,
                        date=current_date,
                        is_absent=True
                    )
            #This code will check for half days and if there are no presents so it will mark absent
            for employee in employees:
                leave_applications = LeaveApplication.objects.filter(employee=employee, leave_status=1)  # Only consider approved leaves
                for leave_app in leave_applications:
                    from_date = leave_app.leave_from_date
                    to_date = leave_app.leave_to_date
                    from_time = leave_app.leave_from_time
                    to_time = leave_app.leave_to_time
                    time_9am = time(hour=9)
                    time_6pm = time(hour=18)
                    if from_date != to_date:
                        if from_time == time_6pm:
                            check_attendance(employee, from_date, from_date)
                        if to_time == time_9am:
                            check_attendance(employee, to_date, to_date)
                    if from_date == to_date:
                        if (from_time == time_6pm and  to_time == time_6pm) or (to_time == time_9am and from_time == time_9am):
                            check_attendance(employee, from_date, from_date)
    
    except Exception as e:
        logger.error("Error in scheduled task: {}".format(e))

def check_attendance(employee, start_date, end_date):
    current_date = timezone.now().date()
    attendance_exists = Attendance.objects.filter(employee=employee, date__range=[start_date, end_date]).exists()
    
    if start_date == current_date or end_date == current_date:
        
        if not attendance_exists:
            
            check_in_time = time(0, 0, 0)
            Attendance.objects.create(
                employee=employee,
                date=current_date,
                clock_in=check_in_time,
                clock_out=check_in_time,
                is_absent=True
            )