from datetime import datetime, timedelta ,date
import string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import HttpResponse

from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML
from core import settings

from datetime import datetime, timedelta

from employee.forms import CustomPasswordChangeForm
from hr.admin import Onboarding
from hr.models import Company, CompanyBranch, Onboarding
from payroll.models import Monthly_salary, Payroll
from employee.models import (Attendance, Department, Designation, Employee, Gender, LeaveApplication, LeaveBalance, Position, ResignApplication)

from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
import logging
logger = logging.getLogger(__name__)
from django import template
register = template.Library()

random_pass_generator = string.ascii_letters + string.digits

def get_session(request):
    employee_name = request.session.get('employee_name', '')
    department = request.session.get('department', '')
    designation = request.session.get('designation', '')
    documents_id = request.session.get('documents_id', '')
    emp_id = request.session.get('emp_id', '')
    reporting_take = request.session.get('reporting_take', '')
    
    profile_pic = None
    if documents_id:
        try:
            profile_pic = Onboarding.objects.get(doc_id=documents_id)
        except Onboarding.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error retrieving profile pic: {e}")

     # Fetch the company logo
    company = Company.objects.first()  # Adjust the query as needed to get the correct company

    company_logo = company.logo.url if company and company.logo else None
    company_name = company.name if company else "Default Company Name"
            
    context = {
        'employee_name': employee_name,
        'department': department,
        'designation': designation,
        'profile_pic': profile_pic,
        'emp_id': emp_id,
        'reporting_take':reporting_take,
        'company_logo': company_logo,  # Add company logo to the context
        'company_name': company_name,
    }

    if employee_name and department and designation and emp_id:
        attendance = Attendance.objects.filter(employee=request.user.emp_user, date=date.today()).first()
        if attendance:
            context['clock_intime'] = attendance.clock_in
            context['clockedin'] = True if attendance.clock_in and not attendance.clock_out else False
        else:
            context['clockedin'] = False

    return context

@login_required(login_url=reverse_lazy('accounts:login'))
def dash(request):
    employee = Employee.objects.get(emp_id=request.user)
    attendance = Attendance.objects.filter(employee=employee)
    # attendance=Attendance.objects.all()
    context={
        'attendance':attendance,
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'employee/dashboard.html', context)


@login_required(login_url=reverse_lazy('accounts:login'))
def rmdash(request):

    try:
        logged_in_employee = Employee.objects.get(emp_id=request.user)
        
        # Initialize variables for counting leave statuses
        approveLeaves = pendingLeaves = rejectedLeaves = 0
        
        # Check if the logged-in employee has reporting_take == True
        if logged_in_employee.reporting_take:
            logged_in_department = logged_in_employee.department
            
            # Filter leave applications based on conditions
            if logged_in_employee.reporting_take:
                employee_leaves = LeaveApplication.objects.filter(
                    Q(employee__reporting_to=logged_in_employee) |
                    Q(employee=logged_in_employee, employee__reporting_take=True)
                ).order_by('-id')
                # Count leave statuses
                approveLeaves = employee_leaves.filter(leave_status=1).count()
                pendingLeaves = employee_leaves.filter(leave_status=2).count()
                rejectedLeaves = employee_leaves.filter(leave_status=3).count()
            else:
                if logged_in_employee.reporting_to:
                    report_manager = logged_in_employee.reporting_to
                    employee_leaves = LeaveApplication.objects.filter(
                        employee__department=logged_in_employee.department,
                        employee__reporting_to=report_manager
                    ).order_by('-id')
            
            context = {
                'employee_leaves': employee_leaves,
                'logged_in_employee': logged_in_employee.name,
                'logged_in_department': logged_in_department,
                'approveLeaves': approveLeaves,
                'pendingLeaves': pendingLeaves,
                'rejectedLeaves': rejectedLeaves,
            }
            context.update(get_session(request))  # Assuming get_session retrieves additional context
            request.session.save()

            return render(request, 'reportingmanager/rmdashboard.html', context)
    except Employee.DoesNotExist:
        return render(request, 'errorpages/error500.html') 

@login_required
def request_regularization(request):
    print(request.POST)
    
    
    filterdate =  datetime.strptime(request.POST.get('dateSelected'), '%d-%m-%Y')
    

    attendance = get_object_or_404(Attendance, date=filterdate,employee=request.user.emp_user)
    
    if request.method == 'POST':
        clock_in_time = request.POST.get('clockInTime')
        clock_out_time = request.POST.get('clockOutTime')

        attendance.regularization_requested = True
        attendance.requested_clock_in = clock_in_time
        attendance.requested_clock_out = clock_out_time
     
        attendance.save()
        
        return HttpResponse("success")


def approve_regularization(request, id):

     # Ensure the user is a manager
    # if not request.user.is_manager:
    #     return redirect('access_denied')


    attendance = get_object_or_404(Attendance, id=id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            attendance.regularized = True
            attendance.regularization_approved = True
            attendance.clock_in = attendance.requested_clock_in
            attendance.clock_out = attendance.requested_clock_out
            
            # Convert requested_clock_in and requested_clock_out to datetime.datetime objects
            if attendance.requested_clock_in and attendance.requested_clock_out:
                clock_in = datetime.combine(attendance.date, attendance.requested_clock_in)
                clock_out = datetime.combine(attendance.date, attendance.requested_clock_out)
                
                # Calculate total hours worked
                total_seconds = (clock_out - clock_in).total_seconds()
                total_hours = total_seconds / 3600
                
                # Determine if it's full day, half day, or not absent
                if total_hours >= 8:
                    attendance.is_full_day = True
                    attendance.is_half_day = False
                    attendance.is_absent = False
                elif total_hours >= 4:
                    attendance.is_full_day = False
                    attendance.is_half_day = True
                    attendance.is_absent = False
                else:
                    attendance.is_full_day = False
                    attendance.is_half_day = False
                    attendance.is_absent = True
            else:
                return HttpResponseBadRequest("Cannot calculate hours: requested_clock_in or requested_clock_out is None.")
                
        elif action == 'reject':
            attendance.regularization_approved = False
        
        attendance.regularization_requested = False
        attendance.save()
        
        return redirect('employee:leaves_lists')

    return render(request, 'hr/leaveapproval.html', {'attendance': attendance})



@login_required(login_url=reverse_lazy('accounts:login'))
def attendance(request):
    logged_in_user = request.user

    if logged_in_user.is_authenticated:
        try:
            employee_regularization = Attendance.objects.filter(
            regularization_requested=True
            ).order_by('id')
        
        # Initialize variables for counting leave statuses
            approveLeaves = pendingLeaves = rejectedLeaves = 0

            logged_in_employee = Employee.objects.get(emp_id=logged_in_user)
            employee = logged_in_employee.emp_id
            logged_in_department = logged_in_employee.department

            leavedata = LeaveApplication.objects.filter(employee = employee)
            attendances = Attendance.objects.filter(employee=employee)
            total_absents = (attendances.filter(is_absent=True).count() + 
                     0.5 * attendances.filter(is_half_day=True).count())
            total_presents = (attendances.filter(is_full_day=True).count() + 
                      0.5 * attendances.filter(is_half_day=True).count())

            context = {'logged_in_department': logged_in_department, 'leavedata':leavedata,'total_absents': total_absents,
            'total_presents':total_presents,'employee_regularization':employee_regularization}

            context.update(get_session(request))  # Call get_session to retrieve the dictionary
            request.session.save()
            return render(request, 'employee/attendance.html', context)
        except Employee.DoesNotExist:
            return render(request, 'errorpages/error500.html')
    else:
        return render(request, 'login.html')

@login_required(login_url=reverse_lazy('accounts:login'))
def mark_clockIn(request, emp_id):
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    if request.method == 'POST':
        current_time = datetime.now()  # Fetches current_time's date in the local timezone
        
        existing_attendance = Attendance.objects.filter(
            employee=employee, date=current_time.date()
        ).exists()
        
        if existing_attendance:
            return JsonResponse({'error': 'You have already clocked in today'}) # Fetches the current time in the local timezone

        new_entry = Attendance.objects.create(
            employee=employee,
            clock_in=current_time.time(),
            date=current_time.date(),
            latitude= request.POST.get('latitude') + ", " + request.POST.get('longitude'),
        )
        return JsonResponse({'success': 'Attendance marked as clocked in'})

    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required(login_url=reverse_lazy('accounts:login'))
def mark_clockOut(request, emp_id):
    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        today = timezone.now()
        
        existing_entry = Attendance.objects.filter(
            employee=employee, date=today.date()
        ).first()
        
        if not existing_entry:
            return JsonResponse({'error': 'You have not clocked in yet for today'})

        if existing_entry.clock_out:
            return JsonResponse({'error': 'You have already clocked out for today'})

        existing_entry.clock_out = today.time()
        existing_entry.longitude= request.POST.get('latitude') + ", " + request.POST.get('longitude')
        existing_entry.save()

        return JsonResponse({'success': 'Attendance marked as clocked out'})

    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required(login_url=reverse_lazy('accounts:login'))
def employee_attendance(request, employee_id):
    # Get attendance data for the specified employee
    attendance_data = Attendance.objects.filter(employee_id=employee_id)
    # Prepare the data in a format that can be sent to the frontend
    formatted_attendance = []
    for attendance in attendance_data:
        formatted_attendance.append({
            'date':attendance.date,
            'clock_in': attendance.clock_in.strftime('%H:%M') if attendance.clock_in else None,
            'clock_out': attendance.clock_out.strftime('%H:%M') if attendance.clock_out else None,
            'is_full_day': attendance.is_full_day,
            'is_half_day': attendance.is_half_day,
            'is_absent': attendance.is_absent
        })
    return JsonResponse({'attendance_data': formatted_attendance})

@login_required(login_url=reverse_lazy('accounts:login'))
def employee_leave_data(request, employee_id):
    # Get leave data for the specified employee
    leave_data = LeaveApplication.objects.filter(employee_id=employee_id)
    # Prepare the data in a format that can be sent to the frontend
    formatted_leave_data = []
    for leave in leave_data:
        formatted_leave_data.append({
            'leave_from_date': leave.leave_from_date.strftime('%Y-%m-%d'),
            'leave_from_time': leave.leave_from_time.strftime('%H:%M'),
            'leave_to_date': leave.leave_to_date.strftime('%Y-%m-%d'),
            'leave_to_time': leave.leave_to_time.strftime('%H:%M'),
            'leave_status': leave.leave_status,
            # Include other relevant fields from LeaveApplication model if needed
        })
    
    return JsonResponse({'leave_data': formatted_leave_data})

@login_required(login_url=reverse_lazy('accounts:login'))
def apply_leave(request, emp_id):
   
    employee = get_object_or_404(Employee, emp_id=emp_id)

    if request.method == 'POST':
        if request.POST.get("leave_from"):
            parsed_date = (request.POST.get("leave_from"))
            leave_from = datetime.strptime(parsed_date,"%d-%m-%Y").date()
        else:
            leave_from = None
            
        leave_from_time = request.POST.get('select_Time_From')
        
        if request.POST.get("leave_to"):
            parsed_date = (request.POST.get("leave_to"))
            leave_to = datetime.strptime(parsed_date,"%d-%m-%Y").date()
        else:
            leave_to = None
            
        leave_to_time = request.POST.get('select_Time_To')
        leave_type = request.POST.get('leave_type')
        leave_reason = request.POST.get('leave_reason')

        leave_from_date_count = datetime.strptime(leave_from, '%Y-%m-%d')
        leave_to_date_count = datetime.strptime(leave_to, '%Y-%m-%d')

        total_days = (leave_to_date_count - leave_from_date_count).days + 1

        # Adjust total days if leave starts at 18:45 or ends at 10:00
        if leave_from_time == '18:45':
            total_days -= 0.5
        if leave_to_time == '10:00':
            total_days -= 0.5

        employee = Employee.objects.get(emp_id=emp_id)
        leave_balance = LeaveBalance.objects.get(employee=employee)
        if total_days >= leave_balance.total_leaves:
            return JsonResponse({'error': 'You can only apply for {} days leave'.format(leave_balance.total_leaves)})

        # Convert leave_from and leave_to to datetime objects
        leave_from_date = datetime.strptime(leave_from, '%Y-%m-%d')
        leave_to_date = datetime.strptime(leave_to, '%Y-%m-%d')

        overlapping_leave = LeaveApplication.objects.filter(
            employee=employee,
            leave_from_date__lte=leave_to_date,
            leave_to_date__gte=leave_from_date
        ).exists()

        if overlapping_leave:
            return JsonResponse({'error': 'Leave already applied for these dates'})  

        leave_application = LeaveApplication.objects.create(
            employee=employee,
            leave_from_date=leave_from_date,
            leave_from_time=leave_from_time,
            leave_to_date=leave_to_date,
            leave_to_time=leave_to_time,
            leave_type=leave_type,
            leave_reason=leave_reason
        )

        return JsonResponse({'success': 'Leave applied successfully'})
    return JsonResponse({'error': 'Invalid Request, Kindly check leave dates and time.'})

def delete_leave(request, leaveID):
    try:
        leave_instance = get_object_or_404(LeaveApplication, id=leaveID)
        leave_instance.delete()
        return JsonResponse({'success': 'Leave deleted successfully'})
    except LeaveApplication.DoesNotExist:
        return JsonResponse({'error': 'Leave not found'}, status=404)


def leaves_lists(request):
    try:
        logged_in_employee = Employee.objects.get(emp_id=request.user)

        employee_regularization = Attendance.objects.filter(
            regularization_requested=True
        ).order_by('id')
        
        # Initialize variables for counting leave statuses
        approveLeaves = pendingLeaves = rejectedLeaves = 0
        
        # Check if the logged-in employee has reporting_take == True
        if logged_in_employee.reporting_take or logged_in_employee.department.name in ['Human Resource','Admin']:
            logged_in_department = logged_in_employee.department
            
            # Filter leave applications based on conditions
            if logged_in_employee.reporting_take or logged_in_employee.department.name in ['Human Resource','Admin']:
                employee_leaves = LeaveApplication.objects.filter(
                    Q(employee__reporting_to=logged_in_employee) |
                    Q(employee=logged_in_employee)
                   # ,leave_status=2  # Filter for pending leaves
                ).order_by('id') 
                # Count leave statuses
                approveLeaves = employee_leaves.filter(leave_status=1).count()
                pendingLeaves = employee_leaves.filter(leave_status=2).count()
                rejectedLeaves = employee_leaves.filter(leave_status=3).count()

                
            else:
                if logged_in_employee.reporting_to:
                    report_manager = logged_in_employee.reporting_to
                    employee_leaves = LeaveApplication.objects.filter(
                        employee__department=logged_in_employee.department,
                        employee__reporting_to=report_manager
                       # ,leave_status=2  # Filter for pending leaves
                    ).order_by('id')  # Order by last created ID
            
            context = {
                'employee_leaves': employee_leaves,
                'logged_in_employee': logged_in_employee.name,
                'logged_in_department': logged_in_department,
                'approveLeaves': approveLeaves,
                'pendingLeaves': pendingLeaves,
                'rejectedLeaves': rejectedLeaves,
                'employee_regularization':employee_regularization,
            }
            context.update(get_session(request))  # Assuming get_session retrieves additional context
            request.session.save()

            return render(request, 'hr/leaveapproval.html', context)
    except Employee.DoesNotExist:
        return render(request, 'errorpages/error500.html')   # Render an error template or handle as needed


@login_required(login_url=reverse_lazy('accounts:login'))
def apply_resign(request, employee_id):
    employee = get_object_or_404(Employee, emp_id=employee_id)
    if request.method == 'POST':
        if request.POST.get("resign_date"):
            parsed_date = (request.POST.get("resign_date"))
            resign_date = datetime.strptime(parsed_date,"%d-%m-%Y").date()
        else:
            resign_date = None
            
        if request.POST.get("last_date"):
            parsed_date = (request.POST.get("last_date"))
            last_date = datetime.strptime(parsed_date,"%d-%m-%Y").date()
        else:
            last_date = None
            
        resign_reason = request.POST.get('resign_reason')
        resign_application = ResignApplication.objects.create(
            employee=employee,
            resign_date=resign_date,
            last_date=last_date,
            resign_reason=resign_reason,
        )
        messages.success(request, 'Resign applied successfully!')
        return redirect('employee:view_profile')
    return render(request, 'employee/employeeprofile.html')

def resign_lists(request):
    try:
        logged_in_employee = Employee.objects.get(emp_id=request.user)
        # Check if the logged-in employee has reporting_take == True
        logged_in_employee.name
        if logged_in_employee.reporting_take or logged_in_employee.department.name in ['Human Resource','Admin']:
            logged_in_department = logged_in_employee.department  # Fetch department from session
            employee_resigns = None  # Default value if conditions don't match
            if logged_in_department.name == logged_in_employee.department.name:
                if logged_in_employee.reporting_take or logged_in_employee.department.name in ['Human Resource','Admin']:
                    employee_resigns = ResignApplication.objects.filter(employee__department__name=logged_in_department)
    
                    approveResigns = employee_resigns.filter(resign_status=1).count()
                    pendingResigns = employee_resigns.filter(resign_status=2).count()
                    rejectedResigns = employee_resigns.filter(resign_status=3).count()
            else: 
                if logged_in_employee.reporting_to:
                    report_manager = logged_in_employee.reporting_to
                    employee_resigns = ResignApplication.objects.filter(
                        employee__department=logged_in_employee.department,
                        employee__reporting_to=report_manager
                    )   
            context = {'employee_resigns': employee_resigns,
                       'logged_in_employee':logged_in_employee.name, 
                       'logged_in_department':logged_in_department,
                       'approveResigns':approveResigns,
                       'pendingResigns':pendingResigns,
                       'rejectedResigns':rejectedResigns,}
            
            context.update(get_session(request))  # Call get_session to retrieve the dictionary
            request.session.save()

            return render(request, 'hr/resignapproval.html',context)
        return render(request, 'errorpages/error500.html')  # You can replace 'error_page.html' with the appropriate error template
    except Employee.DoesNotExist:
        return render(request, 'errorpages/error500.html')  # Render an error template or handle as needed
    
def update_leave_status(request):
    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        selected_status = request.POST.get('selected_status')
        remarks = request.POST.get('remarks')
        
        
        # Perform the necessary logic here based on the received data
        try:
            # Get the LeaveApplication object
            leave_application = LeaveApplication.objects.get(id=leave_id)
            leave_application.leave_status = selected_status
            leave_application.leave_reason = remarks
            leave_application.save()

            leave_from_date = leave_application.leave_from_date
            
            leave_to_date = leave_application.leave_to_date
            
            if selected_status == '1':
                attendance_records = Attendance.objects.filter(date__range=[leave_from_date, leave_to_date])
                
                for record in attendance_records:
                    record.is_on_leave = True
                    record.is_full_day = False
                    record.is_half_day = False
                    record.is_absent = False
                    record.save()
            
            if selected_status != '1':
                attendance_records = Attendance.objects.filter(date__range=[leave_from_date, leave_to_date])
                
                for record in attendance_records:
                    record.is_on_leave = False
                    record.save()
             
            return JsonResponse({'success': 'Leave status updated successfully'})
        except LeaveApplication.DoesNotExist:
            return JsonResponse({'error': 'Leave application not found'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
    
def update_resign_status(request):
    if request.method == 'POST':
        resign_id = request.POST.get('resign_id')
        selected_status = request.POST.get('selected_status')
        remarks = request.POST.get('remarks')
        
        if request.POST.get("last_date"):
            parsed_date = (request.POST.get("last_date"))
            last_date = datetime.strptime(parsed_date, "%Y-%m-%d").date()
        else:
            last_date = None
        
        try:
            resign_application = ResignApplication.objects.get(id=resign_id)
            resign_application.resign_status = selected_status
            resign_application.resign_reason = remarks
            
            if selected_status == '1':  # If status is Approved
                resign_application.last_date = last_date 
            else:
                # If status is not Approved, remove the last date
                resign_application.last_date = None
                
            resign_application.save()

            return JsonResponse({'success': 'Resign status updated successfully'})
        except ResignApplication.DoesNotExist:
            return JsonResponse({'error': 'Resign application not found'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def delete_resign_list(request, resign_list_id):
    if request.method == 'POST':
        try:
            resign_list = ResignApplication.objects.get(pk=resign_list_id)
            resign_list.delete()
            return JsonResponse({'success': 'ResignApplication list deleted successfully'})
        except ResignApplication.DoesNotExist:
            return JsonResponse({'error': 'ResignApplication list not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    


def calculate_paid_leave_days(leave, month, year):
    leave_fromdate = leave.leave_from_date
    leave_fromtime = leave.leave_from_time
    leave_todate = leave.leave_to_date
    leave_totime = leave.leave_to_time
    
    total_full_days = 0
    total_half_days = 0
    paid_leave_total = 0

    leave_from_datetime = datetime.combine(leave_fromdate, leave_fromtime)
    leave_to_datetime = datetime.combine(leave_todate, leave_totime)

    time_9_am = datetime.strptime('10:00', '%H:%M').time()
    time_6_pm = datetime.strptime('18:45', '%H:%M').time()

    start_date_month = datetime.combine(leave.leave_from_date, datetime.min.time())
    end_date_month = datetime.combine(leave.leave_to_date, datetime.min.time())

    if start_date_month.month != end_date_month.month:
        # Calculate total days for the respective months
        leave_start_datetime = datetime.combine(leave_fromdate, datetime.min.time())
        days_in_start_date_month = (datetime(start_date_month.year, start_date_month.month + 1, 1) - leave_start_datetime).days
        days_in_end_date_month = end_date_month.day

        if leave_fromtime == time_9_am:
            days_in_start_date_month
        elif leave_fromtime == time_6_pm:
            days_in_start_date_month = days_in_start_date_month - 0.5
        
        if leave_totime == time_9_am:
            days_in_end_date_month = days_in_end_date_month - 0.5
        elif leave_totime == time_6_pm:
            days_in_end_date_month

        if leave_fromdate.month == month and leave_fromdate.year == year:   
            paid_leave_total += days_in_start_date_month
        if leave_todate.month == month and leave_todate.year == year:
            paid_leave_total+= days_in_end_date_month
    else:
        if leave_fromdate == leave_todate:
            if leave_fromtime == time_9_am and leave_totime == time_6_pm:
                total_full_days += 1
            elif leave_fromtime == time_9_am and leave_totime == time_9_am:
                total_half_days += 0.5
            elif leave_fromtime == time_6_pm and leave_totime == time_6_pm:
                total_half_days += 0.5
        else:
            if leave_fromtime == time_9_am and leave_totime == time_6_pm:
              total_full_days += 1

            else:
                if leave_fromtime == time_6_pm:
                  total_half_days += 0.5

                elif leave_fromtime == time_9_am:
                  total_full_days += 1

            if leave_totime == time_9_am:
                total_half_days += 0.5

            if leave_totime == time_6_pm:
                total_full_days += 1

        # Calculate full days in between start and end dates
        current_date = leave_from_datetime + timedelta(days=1)

        while current_date < leave_to_datetime:
            total_full_days += 1
            current_date += timedelta(days=1)


        paid_leave_total = total_full_days + total_half_days
        if leave_fromdate != leave_todate:
            if leave_fromtime == time_9_am and leave_totime == time_6_pm:
                paid_leave_total = paid_leave_total - 1

        if start_date_month.month != end_date_month.month and start_date_month.year == year:
            paid_leave_total = paid_leave_total + days_in_end_date_month

    return paid_leave_total

def get_half_day_details(leave):
    leave_fromdate = leave.leave_from_date
    leave_fromtime = leave.leave_from_time
    leave_todate = leave.leave_to_date
    leave_totime = leave.leave_to_time

    half_day_details = []

    # Scenario 1: where leave_from_date and leave_to_date dates are same and leave_from_time and leave_to_time are same
    if leave_fromdate == leave_todate and leave_fromtime == leave_totime:
        half_day_details.append({'date': leave_fromdate, 'time': leave_fromtime})

    # Scenario 2: where leave_from_date and leave_to_date dates are different and leave_from_time is 18:45
    if leave_fromdate != leave_todate and leave_fromtime == datetime.strptime('18:45', '%H:%M').time():
        half_day_details.append({'date': leave_fromdate, 'time': leave_fromtime})

    # Scenario 3: where leave_from_date and leave_to_date dates are different and leave_to_time is 10:00
    if leave_fromdate != leave_todate and leave_totime == datetime.strptime('10:00', '%H:%M').time():
        half_day_details.append({'date': leave_todate, 'time': leave_totime})

    return half_day_details

def check_attendance(all_half_day_details, employee):
    false_count = 0

    for detail in all_half_day_details:
        date = detail['date']
        # Check if the date exists in Attendance model and has clock_in and clock_out times
        attendances = Attendance.objects.filter(employee=employee, date=date, clock_in__isnull=False, clock_out__isnull=False)
        if attendances.exists():
            # Iterate over each attendance record for the date
            for attendance_obj in attendances:
                
                # Check if both clock_in and clock_out times are '00:00:00'
                clock_in = attendance_obj.clock_in
                clock_out = attendance_obj.clock_out

                if clock_in == datetime.min.time() and clock_out == datetime.min.time():
                    false_count += 0.5
        else:
            false_count += 0.5

    return false_count

def calculate_attendance_halfday_count(employee, month, paid_leaves, year):
    attendance_halfday_count = 0

    for attendance in Attendance.objects.filter(employee=employee, is_half_day=True, date__month=month, date__year=year):
        attendance_date = attendance.date
        attendance_is_within_leave_range = any(
            leave.leave_from_date <= attendance_date <= leave.leave_to_date 
            for leave in paid_leaves
        )
        if not attendance_is_within_leave_range:
            attendance_halfday_count += 0.5
    return attendance_halfday_count

def remainingLeaves(allLeavesObject, employee, year):
    total_remaining_leave_days = 0
    all_half_day_details = []
    for leave in allLeavesObject:
        leave_from_datetime = datetime.combine(leave.leave_from_date, leave.leave_from_time)
        leave_to_datetime = datetime.combine(leave.leave_to_date, leave.leave_to_time)

        total_full_days = 0
        total_half_days = 0

        time_9_am = datetime.strptime('10:00', '%H:%M').time()
        time_6_pm = datetime.strptime('18:45', '%H:%M').time()

        if leave.leave_from_date == leave.leave_to_date:
            if leave.leave_from_time == time_9_am and leave.leave_to_time == time_6_pm:
                total_full_days += 1
            elif leave.leave_from_time == time_9_am and leave.leave_to_time == time_9_am:
                total_half_days += 0.5
            elif leave.leave_from_time == time_6_pm and leave.leave_to_time == time_6_pm:
                total_half_days += 0.5
        else:
            if leave.leave_from_time == time_9_am and leave.leave_to_time == time_6_pm:
                total_full_days += 1
            else:
                if leave.leave_from_time == time_6_pm:
                    total_half_days += 0.5
                elif leave.leave_from_time == time_9_am:
                    total_full_days += 1
            
            if leave.leave_to_time == time_9_am:
                total_half_days += 0.5
            elif leave.leave_to_time == time_6_pm:
                total_full_days += 1

        current_date = leave_from_datetime + timedelta(days=1)
        while current_date < leave_to_datetime:
            total_full_days += 1
            current_date += timedelta(days=1)

        paid_leave_total = total_full_days + total_half_days

        if leave.leave_from_date != leave.leave_to_date:
            if leave.leave_from_time == time_9_am and leave.leave_to_time == time_6_pm:
                paid_leave_total -= 1
        
        total_remaining_leave_days += paid_leave_total

        #This code will check the data of attendance with date and time and give half day dates
        leave_fromdate = leave.leave_from_date
        leave_fromtime = leave.leave_from_time
        leave_todate = leave.leave_to_date
        leave_totime = leave.leave_to_time

        half_day_details = []
        # Scenario 1: where leave_from_date and leave_to_date dates are same and leave_from_time and leave_to_time are same
        if leave_fromdate == leave_todate and leave_fromtime == leave_totime:
            half_day_details.append({'date': leave_fromdate, 'time': leave_fromtime})

        # Scenario 2: where leave_from_date and leave_to_date dates are different and leave_from_time is 18:45
        if leave_fromdate != leave_todate and leave_fromtime == datetime.strptime('18:45', '%H:%M').time():
            half_day_details.append({'date': leave_fromdate, 'time': leave_fromtime})

        # Scenario 3: where leave_from_date and leave_to_date dates are different and leave_to_time is 10:00
        if leave_fromdate != leave_todate and leave_totime == datetime.strptime('10:00', '%H:%M').time():
            half_day_details.append({'date': leave_todate, 'time': leave_totime})
        
        all_half_day_details.extend(half_day_details)
    
    false_count = 0
    for detail in all_half_day_details:
        date = detail['date']
        # Check if the date exists in Attendance model and has clock_in and clock_out times
        attendances = Attendance.objects.filter(employee=employee, date=date, clock_in__isnull=False, clock_out__isnull=False)

        if attendances.exists():
            # Iterate over each attendance record for the date
            for attendance_obj in attendances:
                # Check if both clock_in and clock_out times are '00:00:00'
                clock_in = attendance_obj.clock_in
                clock_out = attendance_obj.clock_out

                if clock_in == datetime.min.time() and clock_out == datetime.min.time():
                    false_count += 0.5
    total_remaining_leave_days -= false_count                     

    attendance_halfday_count = 0
    for attendance in Attendance.objects.filter(employee=employee, is_half_day=True, date__year=year):
        attendance_date = attendance.date
        attendance_is_within_leave_range = any(
            leave.leave_from_date <= attendance_date <= leave.leave_to_date 
            for leave in allLeavesObject
        )
        if not attendance_is_within_leave_range:
            attendance_halfday_count += 0.5
    total_remaining_leave_days += attendance_halfday_count
    return total_remaining_leave_days #CURRENTLY THIS RETURNS THE TOTAL LEAVES TAKEN.


def employee_monthly_data(request, employee_id, year, month):
    employee = get_object_or_404(Employee, emp_id=employee_id)
    total_paid_leaves = 0
    all_half_day_details = []
    
    attendances = Attendance.objects.filter(
        Q(employee=employee),
        Q(date__year=year, date__month=month)
    )
    
    leaves = LeaveApplication.objects.filter(
        Q(employee=employee),
        Q(leave_from_date__year=year, leave_from_date__month=month) |
        Q(leave_to_date__year=year, leave_to_date__month=month)
    )
    
    paid_leaves = leaves.filter(leave_status=1)
    
    for leave in paid_leaves:
        leave_total = calculate_paid_leave_days(leave, month, year)
        total_paid_leaves += leave_total
        
        total_halfdays = get_half_day_details(leave)
        all_half_day_details.extend(total_halfdays)
    
    false_count = check_attendance(all_half_day_details, employee)
    total_paid_leaves -= false_count
    
    attendance_halfday_count = calculate_attendance_halfday_count(employee, month, paid_leaves, year)
    total_paid_leaves += attendance_halfday_count
    
    allLeavesObject = LeaveApplication.objects.filter(
        Q(employee=employee),
        Q(leave_from_date__year=year) | Q(leave_to_date__year=year),
        Q(leave_status=1)
    )
    totalAppliedLeaves = remainingLeaves(allLeavesObject, employee, year)
    
    total_leave_balance = LeaveBalance.objects.get(employee=employee)
    total_leaves_available = total_leave_balance.total_leaves
    
    leave_Balance = total_leaves_available - totalAppliedLeaves
    
    total_absents = attendances.filter(is_absent=True).count()
    total_presents = attendances.filter(is_full_day=True).count()
    total_half_days = attendances.filter(is_half_day=True).count()
    
    data = {
        'totalPaidLeaves': total_paid_leaves,
        'totalAbsents': total_absents,
        'totalPresents': total_presents,
        'totalHalfDays': total_half_days,
        'totalLeaveBalance': leave_Balance
    }
    
    return JsonResponse(data)



@login_required(login_url='accounts:login')
def view_payroll(request):
    user = request.user
    emp_data = get_object_or_404(Employee, emp_user=user)

    # Get all monthly salary slips for the employee
    all_monthly_salaries = Monthly_salary.objects.filter(emp_id=emp_data.emp_id).order_by('-year', '-month')

    # Get distinct years from the salary slips
    distinct_years = all_monthly_salaries.values_list('year', flat=True).distinct()

    try:
        payroll_data = Payroll.objects.get(emp_id=emp_data)
    except Payroll.DoesNotExist:
        payroll_data = None

    # Multiply the basic salary by 12 in the view
    if payroll_data:
        payroll_data.basic_annual = payroll_data.basic * 12

    context = {
        'emp_data': emp_data,
        'payroll_data': payroll_data,
        'all_monthly_salaries': all_monthly_salaries,
        'distinct_years': distinct_years,
    }
    context.update(get_session(request))
    request.session.save()
    return render(request, 'employee/salaryslipdownload.html', context)



@login_required(login_url='accounts:login')
def download_pdf(request, salary_id):
    salary = get_object_or_404(Monthly_salary, id=salary_id)
    companies = Company.objects.all()
    emp_data= Employee.objects.all()
    template_path = 'employee/emppayslip.html'
    context = {'salary': salary, 'companies': companies,'emp_data':emp_data}
    template = get_template(template_path)
    html_string = template.render(context)

    # Create a PDF file
    pdf_file = HTML(string=html_string).write_pdf()

    # Create HTTP response with PDF attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{salary.month}_salary_slip.pdf"'
    response.write(pdf_file)

    return response


def salaryslip_mail(request, salary_id):
    salary = get_object_or_404(Monthly_salary, id=salary_id)
    companies = Company.objects.all()
    emp_data= Employee.objects.all()
    email = salary.emp_id.email
    context = {'salary': salary, 'companies': companies,'emp_data':emp_data}
    # Render HTML template to string
    html_string = render_to_string('employee/emppayslip.html', context)
    
    # Convert the rendered HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf()

    subject = 'Your Monthly Salary Slip'
    message = f"""Dear {salary.emp_id.name},

Please find attached your salary slip for {salary.month} {salary.year}.

If you have any questions, please feel free to contact HR.

Best Regards,
Your Company Name
"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    # Create email
    email_message = EmailMessage(subject, message, email_from, recipient_list)
    
    # Attach PDF
    email_message.attach(f'Salary_Slip_{salary.month}_{salary.year}.pdf', pdf_file, 'application/pdf')
    
    try:
        email_message.send()
        logger.info(f"Email sent successfully to {', '.join(recipient_list)}")
        return HttpResponse("Salary slip sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email to {', '.join(recipient_list)}: {e}")
        return HttpResponse("Failed to send salary slip.", status=500)

def password_change(request, emp_id):
    emp_data = get_object_or_404(Employee, emp_user=request.user)
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to prevent automatic logout
            messages.success(request, 'Your password was successfully updated!')
            return redirect('employee:password_change', emp_id=emp_data.emp_id)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {'emp_data': emp_data, 'form': form}
    context.update(get_session(request))
    request.session.save()

    return render(request, 'employee/password_change.html', context)


def view_profile(request):
    user = request.user
    emp_data = Employee.objects.get(emp_id=user)
    payroll_data = Payroll.objects.get(emp_id=emp_data)
    
    emp=Employee.objects.all()
    department_all = Department.objects.all()
    designation= Designation.objects.all()
    gender = Gender.objects.all()
    position_all = Position.objects.all()
    company_branch = CompanyBranch.objects.all()
    
    
     # Get the selected reporting manager
    reporting_manager = emp_data.reporting_to

    # Get all employees who report to the selected reporting manager
    employees_reporting_to_selected_manager = Employee.objects.filter(reporting_to=reporting_manager)


    # Get all monthly salary slips for the employee
    all_monthly_salaries = Monthly_salary.objects.filter(emp_id=emp_data.emp_id).order_by('-year', '-month')


    onboarding_documents = Onboarding.objects.filter(candidate_id=emp_data.candidate_id)
    attendances = Attendance.objects.filter(employee=emp_data)
    total_absents = (attendances.filter(is_absent=True).count() + 
                     0.5 * attendances.filter(is_half_day=True).count())
    total_presents = (attendances.filter(is_full_day=True).count() + 
                      0.5 * attendances.filter(is_half_day=True).count())


    leavedata = LeaveApplication.objects.filter(
                        employee=emp_data
                    )
    
    
    
    resign_data = ResignApplication.objects.filter(employee=emp_data)
    

    context = {
        'emp_data': emp_data,
        'onboarding_documents': onboarding_documents,
        'total_absents': total_absents,
        'total_presents':total_presents,
        'leavedata': leavedata,
        'payroll_data':payroll_data,
        'all_monthly_salaries': all_monthly_salaries,
        'resign_data':resign_data,
        'employees_reporting_to_selected_manager': employees_reporting_to_selected_manager,
        'emp':emp,
        'department_all': department_all,
        'designation':designation,
        'gender':gender,
        'position_all':position_all,
        'company_branch':company_branch,
        'attendances':attendances,
        }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'employee/employeeprofile.html', context)

