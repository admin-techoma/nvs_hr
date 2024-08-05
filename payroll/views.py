import pandas as pd
from django.http import HttpResponse
import calendar
from datetime import datetime, timedelta ,date

from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, ExpressionWrapper, F, Q
from django.http import (HttpResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
# from weasyprint import HTML

from core import settings
from employee.models import Attendance, Employee
from hr.models import Company, Onboarding
from payroll.models import Monthly_salary, Payroll

from .forms import MonthlySalaryForm, PayrollForm
from .models import Monthly_salary

register = template.Library()
@register.filter
def amount_in_words(value):
    return amount_in_words(value)


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
        'company_name': company_name
    }

    if employee_name and department and designation and emp_id:
        attendance = Attendance.objects.filter(employee=request.user.emp_user, date=date.today()).first()
        if attendance:
            context['clock_intime'] = attendance.clock_in
            context['clockedin'] = True if attendance.clock_in and not attendance.clock_out else False
        else:
            context['clockedin'] = False
    print(context)
    return context

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url=reverse_lazy('accounts:login'))
def add_payroll(request, pk):
    emp_data = get_object_or_404(Employee, emp_id=pk)
    payrollemp, created = Payroll.objects.get_or_create(emp_id=emp_data)
    # grade = Grade.objects.all()

    if request.method == 'POST':
        # Directly access the POST data without form validation
        office_email = request.POST.get('office_email')
        

        # Check if required fields are present
        if not office_email :
            return HttpResponse("Office Email required", status=400)

        # Set other fields manually
        payrollemp.emp_id = emp_data
        payrollemp.status = "Active"
        payrollemp.office_email = office_email
        payrollemp.monthly_ctc = request.POST.get('monthly_ctc')
        payrollemp.ctc = request.POST.get('ctc')
        payrollemp.basic = request.POST.get('basic')
        payrollemp.hra = request.POST.get('hra')
        payrollemp.ca = request.POST.get('ca')
        payrollemp.sa = request.POST.get('sa')
        payrollemp.gross_salary = request.POST.get('gross_salary')
        payrollemp.employee_pf = request.POST.get('employee_pf')
        payrollemp.employer_pf = request.POST.get('employer_pf')
        payrollemp.employee_esic = request.POST.get('employee_esic')
        payrollemp.employer_esic = request.POST.get('employer_esic')
        payrollemp.pt = request.POST.get('pt')
        payrollemp.total_deduction = request.POST.get('total_deduction')
        payrollemp.net_salary = request.POST.get('net_salary')
        payrollemp.paymentmode = request.POST.get('paymentmode')
        payrollemp.applicable_from = request.POST.get('applicable_from')
        payrollemp.yearlyctc = request.POST.get('yearlyctc')
        payrollemp.save()

        # Create or update the User object only if it doesn't exist
        office_email = request.POST.get('office_email')
        if not office_email:
            return HttpResponse("Office Email is required", status=400)
        user = User.objects.filter(username=emp_data.emp_id).first()
        if not user:
            user = User.objects.create(username=emp_data.emp_id, email=office_email, first_name=emp_data.first_name, last_name=emp_data.last_name)
            # Set the password for the user
            password = User.objects.make_random_password(length=8)
            user.set_password(password)
            user.save()
            
            # Update the Employee status to "Active"
            emp_data.status = "Active"
            emp_data.email = request.POST.get('email')
            emp_data.office_email = office_email
            emp_data.emp_user = user
            emp_data.save()
            
            # Send email to the employee with username and password
            subject = 'Employee Portal Access Credentials Verification'
            message = f"""Dear {emp_data.name},

            We trust this email finds you well. We would like to inform you that your details have been successfully verified, and we are pleased to provide you with the login credentials for accessing the Employee Portal.

            Here are your login details:
            Office Email ID: {emp_data.office_email}
            Username: {emp_data.emp_id}
            Password: {password}

            Please ensure the confidentiality of your login credentials and do not share them with anyone. If you have any concerns or questions regarding the login process, feel free to reach out to our HR department.

            Thank you for your cooperation, and we hope you find the Employee Portal a valuable resource for your work-related activities.

            Best Regards,
            Techoma Technologies Pvt. Ltd.
            Human Resources Department."""
            
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [emp_data.email]
            send_mail(subject, message, email_from, recipient_list)
        messages.success(request, 'Employee Payroll Create successfully.Employee is Active Now!')
        return redirect('payroll:view_payrolllist')

    else:
        form = PayrollForm()

    context = {
        'emp_data': emp_data, 'form': form,'payroll': payrollemp
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render(request, 'hr/GenratePayroll.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url=reverse_lazy('accounts:login'))
def month_salarylist(request):
    payroll_data = Payroll.objects.all()
    attendance_data=Attendance.objects.all()
    monthly_salary_data = Monthly_salary.objects.all() 
    
    context = {
        'payroll_data': payroll_data,
        'attendance_data':attendance_data,
        'monthly_salary_data': monthly_salary_data, 
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render (request,'hr/salarylist.html',context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url=reverse_lazy('accounts:login'))
def create_salary(request, pk):
    payroll_data = get_object_or_404(Payroll, pk=pk)
    employee = payroll_data.emp_id
    ename = payroll_data.emp_id.name

    current_date = datetime.now()
    current_month = current_date.month  # Get the current month as an integer

    full_days_count = employee.attendance_set.filter(
        is_full_day=True,
        date__year=current_date.year,
        date__month=current_month
    ).count()

    half_days_count = employee.attendance_set.filter(
        is_half_day=True,
        date__year=current_date.year,
        date__month=current_month
    ).count()

    absent_days_count = employee.attendance_set.filter(
        is_absent=True,
        date__year=current_date.year,
        date__month=current_month
    ).count()

    total_absent_days = absent_days_count + 0.5 * half_days_count
    

    fiscal_year = f"{current_date.year - 1}-{current_date.year % 100:02d}" if current_month < 4 else f"{current_date.year}-{(current_date.year + 1) % 100:02d}"

    if request.method == 'POST':
        form = MonthlySalaryForm(request.POST)
        print('Before is_valid =============')
        if form.is_valid():
            
            monthly_salary_instance = form.save(commit=False)
            monthly_salary_instance.payroll_id = payroll_data
            monthly_salary_instance.emp_id = employee
            monthly_salary_instance.name = ename
            monthly_salary_instance.month = datetime(current_date.year, current_date.month, 1).date()  # Set the current month
            monthly_salary_instance.year = datetime(current_date.year, 1, 1).date()  # Set the current year
            monthly_salary_instance.total_full_day = total_absent_days
            monthly_salary_instance.fixed_ctc = request.POST.get('fixed_ctc')
            monthly_salary_instance.fixed_basic = request.POST.get('fixed_basic')
            monthly_salary_instance.fixed_hra = request.POST.get('fixed_hra')
            monthly_salary_instance.fixed_ca = request.POST.get('fixed_ca')
            monthly_salary_instance.fixed_sa = request.POST.get('fixed_sa')
            monthly_salary_instance.fixed_employeepf = request.POST.get('fixed_employeepf')
            monthly_salary_instance.fixed_employerpf = request.POST.get('fixed_employerpf')
            monthly_salary_instance.fixed_employeeesic = request.POST.get('fixed_employeeesic')
            monthly_salary_instance.fixed_employeresic = request.POST.get('fixed_employeresic')
            monthly_salary_instance.fixed_gross_salary = request.POST.get('fixed_gross_salary')
            monthly_salary_instance.fixed_newctc = request.POST.get('fixed_newctc')
            monthly_salary_instance.fixed_professionalTax = request.POST.get('fixed_professionalTax')
            monthly_salary_instance.fixed_total_deducation = request.POST.get('fixed_total_deducation')
            monthly_salary_instance.fixed_netpay = request.POST.get('fixed_netpay')
            monthly_salary_instance.monthly_ctc = request.POST.get('monthly_ctc')
            monthly_salary_instance.monthly_basic = request.POST.get('monthly_basic')
            monthly_salary_instance.monthly_hra = request.POST.get('monthly_hra')
            monthly_salary_instance.monthly_ca = request.POST.get('monthly_ca')
            monthly_salary_instance.monthly_sa = float(request.POST.get('monthly_sa', 0))
            monthly_salary_instance.monthly_employeepf = request.POST.get('monthly_employeepf')
            monthly_salary_instance.monthly_employerpf = request.POST.get('monthly_employerpf')
            monthly_salary_instance.monthly_employeeesic = request.POST.get('monthly_employeeesic')
            monthly_salary_instance.monthly_employeresic = request.POST.get('monthly_employeresic')
            monthly_salary_instance.monthly_gross_salary = request.POST.get('monthly_gross_salary')
            monthly_salary_instance.monthly_newctc = request.POST.get('monthly_newctc')
            monthly_salary_instance.monthly_professionalTax = request.POST.get('monthly_professionalTax')
            monthly_salary_instance.monthly_total_deductions = request.POST.get('monthly_total_deductions')
            monthly_salary_instance.monthly_netpay = request.POST.get('monthly_netpay')
            monthly_salary_instance.monthly_netpayinwords = request.POST.get('monthly_netpayinwords', '')
            monthly_salary_instance.monthly_petrol = request.POST.get('monthly_petrol')
            monthly_salary_instance.monthly_bonus = request.POST.get('monthly_bonus')
            monthly_salary_instance.monthly_incentive = request.POST.get('monthly_incentive', '')
            try:
                monthly_salary_instance.monthly_incentive = float(monthly_salary_instance.monthly_incentive)
            except ValueError:
                print(f"Invalid value for 'monthly_incentive': {monthly_salary_instance.monthly_incentive}")
                # You can handle the error here, e.g., set a default value or add an error to the form
                monthly_salary_instance.monthly_incentive = 0
            monthly_salary_instance.monthly_otherallowance = request.POST.get('monthly_otherallowance')
            monthly_salary_instance.monthly_arrears = request.POST.get('monthly_arrears')
            monthly_salary_instance.monthly_presentdays = request.POST.get('monthly_presentdays')
            monthly_salary_instance.monthly_absentdays = request.POST.get('monthly_absentdays')
            monthly_salary_instance.monthly_unpaiddays = request.POST.get('monthly_unpaiddays')
            monthly_salary_instance.monthly_paiddays = request.POST.get('monthly_paiddays')
            monthly_salary_instance.monthly_weekoffdays = request.POST.get('monthly_weekoffdays')
            monthly_salary_instance.salary_createdon = request.POST.get('salary_createdon')
            if monthly_salary_instance.salary_createdon:
                try:
                    monthly_salary_instance.salary_createdon = datetime.strptime(monthly_salary_instance.salary_createdon, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Invalid value for 'salary_createdon': {monthly_salary_instance.salary_createdon}")
                    # Handle the error, set a default value, or add an error to the form
                    monthly_salary_instance.salary_createdon = datetime.now().date()  # Default value or handle it according to your logic
            else:
                # Handle the case when salary_createdon is None (not provided in the request)
                monthly_salary_instance.salary_createdon = datetime.now().date()
# ...

            monthly_salary_instance.payment_status = request.POST.get('payment_status')
            monthly_salary_instance.remarks = request.POST.get('monthly_salary_instance.remarks', '')
            monthly_salary_instance.total_half_day = request.POST.get('total_half_day')
            monthly_salary_instance.total_present_day = request.POST.get('total_present_day')
            monthly_salary_instance.save()
            return redirect('payroll:month_salarylist')
        else:
            print(' =============', form.errors)
    else:

        form = MonthlySalaryForm()

    context = {
        'payroll_data': payroll_data,
        'fiscal_year': fiscal_year,
        'total_absent_days': total_absent_days,
        'form': form,
        'absent_days_count':absent_days_count,
    }
    context.update(get_session(request))
    request.session.save()

    return render(request, 'hr/GenerateSalaryslip.html', context)


def view_beforegenerate_salary(request,pk):
    # all_payroll_applications = Monthly_salary.objects.all()
    payroll_data =  get_object_or_404(Payroll, pk=pk)
    employee = payroll_data.emp_id
    ename = payroll_data.emp_id.name
    # payroll_data = Payroll.objects.all()
    
    current_date = datetime.now()
    current_month = current_date.month
    total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
    print("total_days_in_month",total_days_in_month)
   # Get the list of days in the month
    days_in_month = list(range(1, total_days_in_month + 1))

    # Initialize counters for Saturdays and Sundays
    saturdays = 0
    sundays = 0

    # Iterate over each day in the month
    for day in days_in_month:
        # Use the weekday() method to get the day of the week (Monday is 0, Sunday is 6)
        day_of_week = (current_date.replace(day=day)).weekday()

        # Check if the day is Saturday (5) or Sunday (6)
        if day_of_week == 5:
            saturdays += 1
        elif day_of_week == 6:
            sundays += 1

    total_saturdays_and_sundays = saturdays + sundays
    # Query total absent days for all employees in the current month and year
    employee_data = Employee.objects.annotate(
        half_days_count=Count('attendance', filter=Q(
            attendance__is_half_day=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        absent_days_count=Count('attendance', filter=Q(
            attendance__is_absent=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        total_absent_days=ExpressionWrapper(
            F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        
        total_paid_days=ExpressionWrapper(
            31 - F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        
        full_days_count=Count('attendance', filter=Q(
        attendance__is_full_day=True,
        attendance__date__year=current_date.year,
        attendance__date__month=current_month
        )),
        
        total_present_days=ExpressionWrapper(
        F('full_days_count') + 0.5 * F('half_days_count'),
        output_field=fields.FloatField()
        ),
        total_half_days=ExpressionWrapper(
        F('half_days_count'),
        output_field=fields.FloatField()
        ),
        ).values('emp_id', 'name', 'total_absent_days', 'total_present_days','total_half_days')

        
        
    # Calculate monthly ctc and payroll_id for each employee
    for employee in employee_data:
        total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

        payroll_obj = Payroll.objects.filter(emp_id=employee['emp_id']).first()
        if payroll_obj and payroll_obj.ctc is not None:
            
            total_absent_days = employee['total_absent_days'] or 0
            monthly_ctc = (payroll_obj.ctc / total_days_in_month) * (total_days_in_month - total_absent_days)
            total_paid_days = total_days_in_month - total_absent_days
            employee['monthly_ctc'] = monthly_ctc
            employee['total_paid_days'] = total_paid_days
            employee['payroll_id'] = payroll_obj.payroll_id
        else:
            employee['monthly_ctc'] = 0
            employee['total_paid_days'] = 0  # Set a default value if payroll_obj or ctc is None
            employee['payroll_id'] = ""  # Set an empty value for payroll_id if payroll_obj is None

    fiscal_year = f"{current_date.year - 1}-{current_date.year % 100:02d}" if current_month < 4 else f"{current_date.year}-{(current_date.year + 1) % 100:02d}"
    
    
    context = {
        'payroll_data': payroll_data,
        'fiscal_year': fiscal_year,
        'employee_data': employee_data,
        'total_saturdays_and_sundays': total_saturdays_and_sundays,
        'total_days_in_month':total_days_in_month,
    }
        

    context.update(get_session(request))
    request.session.save()
    return render(request, 'hr/viewbeforeGenerateSalary.html', context)


def edit_beforegenerate_salary(request,pk):
    # all_payroll_applications = Monthly_salary.objects.all()
    payroll_data =  get_object_or_404(Payroll, pk=pk)
    employee = payroll_data.emp_id
    ename = payroll_data.emp_id.name
    # payroll_data = Payroll.objects.all()
    
    current_date = datetime.now()
    current_month = current_date.month
    total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
   # Get the list of days in the month
    days_in_month = list(range(1, total_days_in_month + 1))

    # Initialize counters for Saturdays and Sundays
    saturdays = 0
    sundays = 0

    # Iterate over each day in the month
    for day in days_in_month:
        # Use the weekday() method to get the day of the week (Monday is 0, Sunday is 6)
        day_of_week = (current_date.replace(day=day)).weekday()

        # Check if the day is Saturday (5) or Sunday (6)
        if day_of_week == 5:
            saturdays += 1
        elif day_of_week == 6:
            sundays += 1

    total_saturdays_and_sundays = saturdays + sundays
    # Query total absent days for all employees in the current month and year
    employee_data = Employee.objects.annotate(
        half_days_count=Count('attendance', filter=Q(
            attendance__is_half_day=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        absent_days_count=Count('attendance', filter=Q(
            attendance__is_absent=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        total_absent_days=ExpressionWrapper(
            F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        total_paid_days=ExpressionWrapper(
            31 - F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        full_days_count=Count('attendance', filter=Q(
        attendance__is_full_day=True,
        attendance__date__year=current_date.year,
        attendance__date__month=current_month
        )),
        total_present_days=ExpressionWrapper(
        F('full_days_count') + 0.5 * F('half_days_count'),
        output_field=fields.FloatField()
        ),
        ).values('emp_id', 'name', 'total_absent_days', 'total_present_days')

    # Calculate monthly ctc and payroll_id for each employee
    for employee in employee_data:
        total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

        payroll_obj = Payroll.objects.filter(emp_id=employee['emp_id']).first()
        if payroll_obj and payroll_obj.ctc is not None:
            total_absent_days = employee['total_absent_days'] or 0
            monthly_ctc = (payroll_obj.ctc / total_days_in_month) * (total_days_in_month - total_absent_days)
            total_paid_days = total_days_in_month - total_absent_days
            employee['monthly_ctc'] = monthly_ctc
            employee['total_paid_days'] = total_paid_days
            employee['payroll_id'] = payroll_obj.payroll_id
        else:
            employee['monthly_ctc'] = 0
            employee['total_paid_days'] = 0  # Set a default value if payroll_obj or ctc is None
            employee['payroll_id'] = ""  # Set an empty value for payroll_id if payroll_obj is None

    fiscal_year = f"{current_date.year - 1}-{current_date.year % 100:02d}" if current_month < 4 else f"{current_date.year}-{(current_date.year + 1) % 100:02d}"
    
    
    context = {
        'payroll_data': payroll_data,
        'fiscal_year': fiscal_year,
        'employee_data': employee_data,
        'total_saturdays_and_sundays': total_saturdays_and_sundays
    }
        

    context.update(get_session(request))
    request.session.save()
    return render(request, 'hr/EditbeforeGenerateSalary.html', context)



from django.db.models import Count, ExpressionWrapper, F, Q, fields
from django.shortcuts import render

from .models import Employee, Monthly_salary, Payroll


def month_salary(request):
    all_payroll_applications = Monthly_salary.objects.all()
    payroll_data = Payroll.objects.all()
    employee = Employee.objects.all()
    payroll_data = Payroll.objects.all()
    
    current_date = datetime.now()
    current_month = current_date.month
    total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

    # Get the list of days in the month
    days_in_month = list(range(1, total_days_in_month + 1))

    # Initialize counters for Saturdays and Sundays
    saturdays = 0
    sundays = 0

    # Iterate over each day in the month
    for day in days_in_month:
        # Use the weekday() method to get the day of the week (Monday is 0, Sunday is 6)
        day_of_week = (current_date.replace(day=day)).weekday()

        # Check if the day is Saturday (5) or Sunday (6)
        if day_of_week == 5:
            saturdays += 1
        elif day_of_week == 6:
            sundays += 1

    total_saturdays_and_sundays = saturdays + sundays
   
    # Query total absent days for all employees in the current month and year
    employee_data = Employee.objects.annotate(
        half_days_count=Count('attendance', filter=Q(
            attendance__is_half_day=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        absent_days_count=Count('attendance', filter=Q(
            attendance__is_absent=True,
            attendance__date__year=current_date.year,
            attendance__date__month=current_month
        )),
        total_absent_days=ExpressionWrapper(
            F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        total_paid_days=ExpressionWrapper(
            31 - F('absent_days_count') + 0.5 * F('half_days_count'),
            output_field=fields.FloatField()
        ),
        full_days_count=Count('attendance', filter=Q(
        attendance__is_full_day=True,
        attendance__date__year=current_date.year,
        attendance__date__month=current_month
        )),
        total_present_days=ExpressionWrapper(
        F('full_days_count') + 0.5 * F('half_days_count'),
        output_field=fields.FloatField()
        ),
        total_half_days=ExpressionWrapper(
        F('half_days_count'),
        output_field=fields.FloatField()
        ),
        ).values('emp_id', 'name', 'doj','total_absent_days', 'total_present_days','total_half_days')

    # Calculate monthly ctc and payroll_id for each employee
    for employee in employee_data:
        
        payroll_obj = Payroll.objects.filter(emp_id=employee['emp_id']).first()
        if payroll_obj and payroll_obj.ctc is not None:
            total_absent_days = employee['total_absent_days'] or 0
            monthly_ctc = (payroll_obj.ctc / total_days_in_month) * (total_days_in_month - total_absent_days)
            total_paid_days = total_days_in_month - total_absent_days
            employee['monthly_ctc'] = monthly_ctc
            employee['total_paid_days'] = total_paid_days
            employee['payroll_id'] = payroll_obj.payroll_id
        else:
            employee['monthly_ctc'] = 0
            employee['total_paid_days'] = 0  # Set a default value if payroll_obj or ctc is None
            employee['payroll_id'] = ""  # Set an empty value for payroll_id if payroll_obj is None

    fiscal_year = f"{current_date.year - 1}-{current_date.year % 100:02d}" if current_month < 4 else f"{current_date.year}-{(current_date.year + 1) % 100:02d}"
    # Get the last 5 days of the month
    last_five_days_of_month = current_date.replace(day=total_days_in_month) - timedelta(days=4)

    # Check if the current date is within the last 5 days of the month
    show_generate_button = current_date >= last_five_days_of_month
    
    if request.method == 'POST' and 'download_button' in request.POST:
        df = pd.DataFrame(list(all_payroll_applications.values()))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="salarygenerate_report.csv"'
        df.to_csv(response, index=False)
        return response
    else:
        context = {
            'payroll_datas': payroll_data,
            'fiscal_year': fiscal_year,
            'employee_data': employee_data,
            'total_saturdays_and_sundays': total_saturdays_and_sundays,
            'show_generate_button': show_generate_button,
            'total_days_in_month':total_days_in_month
        }
        

    context.update(get_session(request))
    request.session.save()

    return render(request, 'hr/GenerateSalary.html', context)

def generate_salary(request):
    # Get the current month and year
    current_month_year = datetime.now().strftime('%B')  # Full month name, e.g., 'February'
    current_year = datetime.now().strftime('%Y')  # Four-digit year, e.g., '2024'

    # Check if salary has been generated for the current month and year
    salary_generated = Monthly_salary.objects.filter(month=current_month_year, year=current_year).exists()

    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        # If salary has not been generated, proceed to generate it
        if not salary_generated:
            print("============================")
            print("                            ")
            print("                            ")
            print(request.POST)
            print("============================")
            print("                            ")
            print("                            ")
            emp_id_list = request.POST.getlist('emp_id')
            print('emp_id: ', emp_id_list)
            payroll_id_list = request.POST.getlist('payroll_id')
            print('payroll_id: ', payroll_id_list)
            name_list = request.POST.getlist('name')
            print('name: ', name_list)
            monthly_ctc_list = request.POST.getlist('monthly_ctc')
            print('monthly_ctc: ', monthly_ctc_list)
            monthly_basic_list = request.POST.getlist('monthly_basic')
            print('monthly_basic: ', monthly_basic_list)
            monthly_hra_list = request.POST.getlist('monthly_hra')
            print('monthly_hra: ', monthly_hra_list)
            monthly_ca_list = request.POST.getlist('monthly_ca')
            print('monthly_ca: ', monthly_ca_list)
            monthly_sa_list = request.POST.getlist('monthly_sa')
            print('monthly_sa: ', monthly_sa_list)
            monthly_employerpf_list =   request.POST.getlist('monthly_employerpf')
            print('monthly_employerpf: ', monthly_employerpf_list)
            monthly_employeresic_list = request.POST.getlist('monthly_employeresic')
            print('monthly_employeresic: ', monthly_employeresic_list)
            monthly_employeepf_list =   request.POST.getlist('monthly_employeepf')
            print('monthly_employeepf: ', monthly_employeepf_list)
            monthly_employeeesic_list = request.POST.getlist('monthly_employeeesic')
            print('monthly_employeeesic: ', monthly_employeeesic_list)
            monthly_professionalTax_list = request.POST.getlist('monthly_professionalTax')
            print('monthly_professionalTax: ', monthly_professionalTax_list)
            monthly_incentive_list = request.POST.getlist('monthly_incentive')
            print('monthly_incentive: ', monthly_incentive_list)
            monthly_loan_other_list = request.POST.getlist('monthly_loan')
            print('monthly_loan: ', monthly_loan_other_list)
            monthly_gross_salary_list= request.POST.getlist('monthly_gross_salary')
            print('monthly_gross_salary: ', monthly_gross_salary_list)
            monthly_newctc_list= request.POST.getlist('monthly_ctc')
            print('monthly_newctc: ', monthly_newctc_list)
            monthly_total_deductions_list= request.POST.getlist('monthly_total_deductions')
            print('monthly_total_deductions: ', monthly_total_deductions_list)
            monthly_netpay_list= request.POST.getlist('monthly_netpay')
            print('monthly_netpay: ', monthly_netpay_list)
            fixed_ctc_list= request.POST.getlist('fixed_ctc')
            print('fixed_ctc: ', fixed_ctc_list)

            fixed_basic_list = request.POST.getlist('fixed_basic')
            print('fixed_basic: ', fixed_basic_list)
            fixed_hra_list = request.POST.getlist('fixed_hra')
            print('fixed_hra: ', fixed_hra_list)
            fixed_ca_list = request.POST.getlist('fixed_ca')
            print('fixed_ca: ', fixed_ca_list)
            fixed_sa_list = request.POST.getlist('fixed_sa')
            print('fixed_sa: ', fixed_sa_list)
            fixed_employeepf_list = request.POST.getlist('fixed_employeepf')
            print('fixed_employeepf: ', fixed_employeepf_list)
            fixed_employerpf_list = request.POST.getlist('fixed_employerpf')
            print('fixed_employerpf: ', fixed_employerpf_list)
            fixed_employeeesic_list = request.POST.getlist('fixed_employeeesic')
            print('fixed_employeeesic: ', fixed_employeeesic_list)
            fixed_employeresic_list = request.POST.getlist('fixed_employeresic')
            print('fixed_employeresic: ', fixed_employeresic_list)
            fixed_gross_salary_list = request.POST.getlist('fixed_gross_salary')
            print('fixed_gross_salary: ', fixed_gross_salary_list)
            fixed_newctc_list = request.POST.getlist('fixed_newctc')
            print('fixed_newctc: ', fixed_newctc_list)
            fixed_professionalTax_list = request.POST.getlist('fixed_professionalTax')
            print('fixed_professionalTax: ', fixed_professionalTax_list)
            fixed_total_deducation_list = request.POST.getlist('fixed_total_deducation')
            print('fixed_total_deducation: ', fixed_total_deducation_list)
            fixed_netpay_list = request.POST.getlist('fixed_netpay')
            print('fixed_netpay: ', fixed_netpay_list)
            remarks_list = request.POST.getlist('remarks')
            print('remarks: ', remarks_list)
            monthly_presentdays_list =  request.POST.getlist('monthly_presentdays')
            print('monthly_presentdays: ', monthly_presentdays_list)
            monthly_absentdays_list= request.POST.getlist('monthly_absentdays')
            print('monthly_absentdays: ', monthly_absentdays_list)
            monthly_halfdays_list= request.POST.getlist('monthly_halfdays')
            print('monthly_halfdays: ', monthly_halfdays_list)
            monthly_paiddays_list= request.POST.getlist('monthly_paiddays')
            print('monthly_paiddays: ', monthly_paiddays_list)
            monthly_weekoffdays_list= request.POST.getlist('monthly_weekoffdays')
            print('monthly_weekoffdays: ', monthly_weekoffdays_list)
            print("                            ")
            print("                            ")
            print("============================")
            # Ensure the lengths of emp_id_list and payroll_id_list are the same
            if len(emp_id_list) == len(payroll_id_list) == len(name_list) == len(fixed_ctc_list) == len(fixed_basic_list)== len(fixed_hra_list)== len(fixed_ca_list)== len(fixed_sa_list)== len(fixed_employeepf_list)== len(fixed_employerpf_list)== len(fixed_employeeesic_list)== len(fixed_employeresic_list)== len(fixed_gross_salary_list)== len(fixed_newctc_list)== len(fixed_professionalTax_list)== len(fixed_total_deducation_list)== len(fixed_netpay_list) == len(monthly_ctc_list) == len(monthly_basic_list) == len(monthly_hra_list) == len(monthly_ca_list) == len(monthly_sa_list) == len(monthly_employerpf_list) == len(monthly_employeresic_list) == len(monthly_employeepf_list) == len(monthly_employeeesic_list) == len(monthly_professionalTax_list) == len(monthly_incentive_list) == len(monthly_loan_other_list) == len(monthly_gross_salary_list) == len(monthly_total_deductions_list) == len(monthly_netpay_list) == len(monthly_newctc_list) ==len(remarks_list) == len(monthly_presentdays_list) == len(monthly_absentdays_list) == len(monthly_halfdays_list) == len(monthly_paiddays_list) == len(monthly_weekoffdays_list) :
                
                # Save data to the Month_salary model
                for emp_id, payroll_id, name ,fixed_ctc,fixed_basic,fixed_hra,fixed_ca,fixed_sa,fixed_employeepf,fixed_employerpf,fixed_employeeesic,fixed_employeresic,fixed_gross_salary,fixed_newctc,fixed_professionalTax,fixed_total_deducation,fixed_netpay,monthly_ctc ,monthly_basic,monthly_hra,monthly_ca,monthly_sa ,monthly_employerpf,monthly_employeresic,monthly_employeepf,monthly_employeeesic,monthly_professionalTax,monthly_incentive,monthly_loan_other,monthly_gross_salary,monthly_total_deductions,monthly_netpay,monthly_newctc,remarks,monthly_presentdays,monthly_absentdays,monthly_halfdays,monthly_paiddays,monthly_weekoffdays in zip(emp_id_list, payroll_id_list, name_list,fixed_ctc_list,fixed_basic_list,fixed_hra_list,fixed_ca_list,fixed_sa_list,fixed_employeepf_list,fixed_employerpf_list,fixed_employeeesic_list,fixed_employeresic_list,fixed_gross_salary_list,fixed_newctc_list,fixed_professionalTax_list,fixed_total_deducation_list,fixed_netpay_list,monthly_ctc_list,monthly_basic_list,monthly_hra_list,monthly_ca_list,monthly_sa_list ,monthly_employerpf_list,monthly_employeresic_list,monthly_employeepf_list,monthly_employeeesic_list,monthly_professionalTax_list,monthly_incentive_list,monthly_loan_other_list,monthly_gross_salary_list,monthly_total_deductions_list,monthly_netpay_list,monthly_newctc_list,remarks_list,monthly_presentdays_list,monthly_absentdays_list,monthly_halfdays_list,monthly_paiddays_list,monthly_weekoffdays_list):
                # emp_id_list, payroll_id_list, name_list,fixed_ctc_list,fixed_basic_list,fixed_hra_list,fixed_ca_list,fixed_sa_list,fixed_employeepf_list,fixed_employerpf_list,fixed_employeeesic_list,fixed_employeresic_list,fixed_gross_salary_list,fixed_newctc_list,fixed_professionalTax_list,fixed_total_deducation_list,fixed_netpay_list,monthly_ctc_list,monthly_basic_list,monthly_hra_list,monthly_ca_list,monthly_sa_list ,monthly_employerpf_list,monthly_employeresic_list,monthly_employeepf_list,monthly_employeeesic_list,monthly_professionalTax_list,monthly_incentive_list,monthly_loan_other_list,monthly_gross_salary_list,monthly_total_deductions_list,monthly_netpay_list,monthly_newctc_list,remarks_list,monthly_presentdays_list,monthly_absentdays_list,monthly_halfdays_list,monthly_paiddays_list,monthly_weekoffdays_list)    
                    if not monthly_incentive:
                        monthly_incentive = 0
                    if not monthly_loan_other:
                        monthly_loan_other = 0
                    print(monthly_ctc)    
                    print(monthly_newctc)    
                    month_salary_instance = Monthly_salary(
                        emp_id=Employee.objects.get(emp_id=emp_id),
                        name=name,
                        fixed_ctc=fixed_ctc,
                        monthly_ctc=monthly_ctc,
                        monthly_basic = monthly_basic,
                        monthly_hra=monthly_hra,
                        monthly_ca=monthly_ca,
                        monthly_sa=monthly_sa,
                        monthly_employerpf=monthly_employerpf,
                        monthly_employeresic=monthly_employeresic,
                        monthly_employeepf=monthly_employeepf,
                        monthly_employeeesic=monthly_employeeesic,
                        monthly_professionalTax=monthly_professionalTax,
                        monthly_incentive=monthly_incentive,
                        monthly_loan_other=monthly_loan_other,
                        monthly_gross_salary = monthly_gross_salary,
                        monthly_newctc=monthly_newctc,
                        monthly_total_deductions=monthly_total_deductions,
                        monthly_netpay=monthly_netpay,
                        monthly_presentdays=monthly_presentdays,
                        monthly_absentdays=monthly_absentdays,
                        monthly_halfdays=monthly_halfdays,
                        monthly_paiddays=monthly_paiddays,
                        monthly_weekoffdays=monthly_weekoffdays,
                        fixed_basic = fixed_basic,
                        fixed_hra = fixed_hra,
                        fixed_ca = fixed_ca,
                        fixed_sa = fixed_sa,
                        fixed_employerpf = fixed_employerpf,
                        fixed_employeresic = fixed_employeresic,
                        fixed_employeepf = fixed_employeepf,
                        fixed_employeeesic = fixed_employeeesic,
                        fixed_newctc=fixed_newctc,
                        fixed_professionalTax = fixed_professionalTax,
                        fixed_gross_salary = fixed_gross_salary,
                        fixed_total_deducation = fixed_total_deducation,
                        fixed_netpay = fixed_netpay,
                        remarks=remarks,
                        payroll_id=payroll_id,
                        month=current_month_year,
                        year=current_year
                        # Add other fields accordingly
                    )
                    month_salary_instance.save()

                # Display success message
                messages.success(request, 'Salary data generated successfully.')
                return redirect('payroll:view_generatesalary')  # Redirect to a success page or another URL
            else:
                # Display an error message if lengths don't match
                messages.error(request, 'Mismatch in emp_id, payroll_id, and name entries.')
                return redirect('payroll:month_salary')  # Redirect to an error page or another URL
        else:
            # Display error message if salary data already exists for the current month and year
            messages.error(request, 'Salary data for this month and year already exists.')
            return redirect('payroll:month_salary')  # Redirect to an error page or another URL

    # Render the template with the salary_generated flag
    return render(request, 'hr/GenerateSalary.html', {'salary_generated': salary_generated})

def month_salaryslip(request,pk):

    monthly_salary_instance = get_object_or_404(Monthly_salary, pk=pk)


    context = {
       'monthly_salary_instance':monthly_salary_instance
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render(request, 'hr/payslip.html', context)

def download_salary_pdf(request, pk):
    # Retrieve the Monthly_salary instance
    salary = get_object_or_404(Monthly_salary, pk=pk)

    template_path = 'employee/emppayslip.html'
    context = {'salary': salary}
    template = get_template(template_path)
    html_string = template.render(context)

    # Create a PDF file
    pdf_file = HTML(string=html_string).write_pdf()

    # Create HTTP response with PDF attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{salary.month}_salary_slip.pdf"'
    response.write(pdf_file)

    return response


from dateutil.relativedelta import relativedelta

def days_in_month(date):
    date = date.replace(day=1)
    next_month = date + relativedelta(months=1)
    return (next_month - date).days

def view_salary(request , pk):

    monthly_salary_instance = get_object_or_404(Monthly_salary, pk=pk)
    context = {
       'payroll_data':monthly_salary_instance,
       'total_days':days_in_month(monthly_salary_instance.salary_createdon)
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render(request, 'hr/EditGenerateSalaryslip.html', context)

def edit_salary(request , id):

    if request.method == 'POST':

        monthly_ctc   = request.POST.get('monthly_ctc')
        monthly_basic   = request.POST.get('monthly_basic')
        monthly_hra   = request.POST.get('monthly_hra')
        monthly_ca   = request.POST.get('monthly_ca')
        monthly_sa   = request.POST.get('monthly_sa')
        monthly_employeepf   = request.POST.get('monthly_employeepf')
        monthly_employerpf   = request.POST.get('monthly_employerpf')
        monthly_employeeesic   = request.POST.get('monthly_employeeesic')
        monthly_employeresic   = request.POST.get('monthly_employeresic')
        monthly_gross_salary   = request.POST.get('monthly_gross_salary')
        monthly_newctc   = request.POST.get('monthly_newctc')
        monthly_professionalTax   = request.POST.get('monthly_professionalTax')
        monthly_total_deductions   = request.POST.get('monthly_total_deductions')
        monthly_netpay   = request.POST.get('monthly_netpay')
        monthly_netpayinwords   = request.POST.get('monthly_netpayinwords')
        monthly_incentive   = request.POST.get('monthly_incentive')
        monthly_loan_other = request.POST.get('monthly_loan_other')
        monthly_paiddays   = request.POST.get('monthly_paiddays')


        
        payroll_data = Monthly_salary.objects.get(id=id)

        payroll_data.monthly_ctc = monthly_ctc
        payroll_data.monthly_basic = monthly_basic
        payroll_data.monthly_hra = monthly_hra
        payroll_data.monthly_ca = monthly_ca
        payroll_data.monthly_sa = monthly_sa
        payroll_data.monthly_employeepf = monthly_employeepf
        payroll_data.monthly_employerpf = monthly_employerpf
        payroll_data.monthly_employeeesic = monthly_employeeesic
        payroll_data.monthly_employeresic = monthly_employeresic
        payroll_data.monthly_gross_salary = monthly_gross_salary
        payroll_data.monthly_newctc = monthly_newctc
        payroll_data.monthly_professionalTax = monthly_professionalTax
        payroll_data.monthly_total_deductions = monthly_total_deductions
        payroll_data.monthly_netpay = monthly_netpay
        payroll_data.monthly_netpayinwords = monthly_netpayinwords
        payroll_data.monthly_incentive = monthly_incentive
        print("monthly_paiddays",monthly_paiddays)
        payroll_data.monthly_loan_other = monthly_loan_other
        payroll_data.monthly_paiddays = monthly_paiddays
    


           
        payroll_data.save()

        
        messages.success(request, 'Salary Update successfully.')
        return redirect('payroll:view_generatesalary')
    else:
        
        # Handle GET request or other cases
       pass




def view_generatesalary(request):
    all_payroll_applications = Monthly_salary.objects.all()

    if request.method == 'POST' and 'download_button' in request.POST:
        # Export data to CSV
        df = pd.DataFrame(list(all_payroll_applications.values()))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="view_generatesalary.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        # Render HTML template
        # Collect unique months and years
        months = all_payroll_applications.values_list('month', flat=True).distinct()
        years = all_payroll_applications.values_list('year', flat=True).distinct()
        
        context = {
            'all_payroll_applications': all_payroll_applications,
            'unique_months': months,
            'unique_years': years,
        }
        context.update(get_session(request))
        request.session.save()
        return render(request, 'hr/view_generatesalary.html', context)


