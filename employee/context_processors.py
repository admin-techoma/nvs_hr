from .models import Onboarding, Company, Attendance
from datetime import datetime, timedelta ,date

def mycontext(request):

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