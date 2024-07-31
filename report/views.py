import os
import zipfile
from datetime import date, datetime, time, timedelta ,date

import fitz
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)

from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from docx import Document

from employee.models import (Attendance, Department, Designation, Employee,
                             Gender, LeaveApplication, Position,
                             ResignApplication)
from hr.models import Company, Interview, Onboarding, candidateResume
from payroll.models import Monthly_salary, Payroll




def get_session(request):
    employee_name = request.session.get('employee_name', '')
    department = request.session.get('department', '')
    designation = request.session.get('designation', '')
    documents_id = request.session.get('documents_id', '')
    emp_id = request.session.get('emp_id', '')
    reporting_take = request.session.get('reporting_take', '')
    session_email = request.session.get('session_email', '')
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
        'session_email':session_email,
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

@login_required(login_url=reverse_lazy('accounts:login'))
def employee_report(request):
  
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/employeereport.html', context)

def employeedata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Employee.objects.filter(doj__range = daterange).values("emp_id","candidate_id","first_name","middle_name","last_name","name","gender__name","address","state","city","country","pin_code","c_address","c_state","c_city","c_country","c_pin_code","email","office_email","company_branch__name","contact_no","other_contact_no","dob","doj","doe","pfno","pf_joining_date","pf_exit_date","uanno","esicno","esic_joining_date","esic_exit_date","pancard_no","aadhaarcard_no","account_no","bank_name","ifsc_code","branch","department__name","designation__name","reporting_to__name","documents_id","status","interview_take","reporting_take","position__name","married_status","blood_group","linkedin_profile","instagram_profile","facebook_profile","esic_apply","pf_apply",))
                    # ("emp_id","candidate_id","name","doj","department__name","designation__name","documents_id","status",))
    return JsonResponse({'data':queryset})


@login_required(login_url=reverse_lazy('accounts:login'))
def attendance_report(request):
  
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/attendanceReport.html', context)

def attendancedata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Attendance.objects.filter(date__range = daterange).values("employee__emp_id","employee__name","date","clock_in","clock_out","is_full_day","is_half_day","is_absent","is_on_leave",))
    return JsonResponse({'data':queryset})




@login_required(login_url=reverse_lazy('accounts:login'))
def leave_report(request):
  
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/LeaveReport.html', context)

def leavedata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(LeaveApplication.objects.filter(leave_from_date__range = daterange).values("employee__emp_id","leave_from_date","leave_from_time","leave_to_date","leave_to_time","leave_type","leave_reason","leave_status",))
    return JsonResponse({'data':queryset})


def view_payrollreport(request):


    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/PayrollReport.html', context)

def payrollreportdata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Payroll.objects.filter(applicable_from__range = daterange).values("payroll_id","emp_id","ctc","basic","hra","ca","sa","employee_pf","employer_pf","employee_esic","employer_esic","pt","gross_salary","total_deduction","net_salary","monthly_ctc","applicable_from","remarks","status","paymentmode","yearlyctc",))
    return JsonResponse({'data':queryset})

def salary_report(request):
  
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/SalaryReport.html', context)

def salarydata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Monthly_salary.objects.filter(salary_createdon__range = daterange).values("payroll_id","emp_id","month","year","salary_createdon","payment_status","remarks","name","fixed_ctc","fixed_basic","fixed_hra","fixed_ca","fixed_sa","fixed_employeepf","fixed_employerpf","fixed_employeeesic","fixed_employeresic","fixed_gross_salary","fixed_newctc","fixed_professionalTax","fixed_total_deducation","fixed_netpay","monthly_ctc","monthly_basic","monthly_hra","monthly_ca","monthly_sa","monthly_employeepf","monthly_employerpf","monthly_employeeesic","monthly_employeresic","monthly_gross_salary","monthly_newctc","monthly_professionalTax","monthly_total_deductions","monthly_netpay","monthly_netpayinwords","monthly_incentive","monthly_loan_other","monthly_presentdays","monthly_absentdays","monthly_halfdays","monthly_unpaiddays","monthly_paiddays","monthly_weekoffdays",))
    return JsonResponse({'data':queryset})


      
def resign_report(request):
    
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/ResignReport.html', context)


def resigndata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(ResignApplication.objects.filter(resign_date__range = daterange).values("employee__emp_id","resign_date","last_date","resign_reason","resign_status",))
    return JsonResponse({'data':queryset})


def document_report(request):
    
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/DocumentReport.html', context)


def documentdata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Onboarding.objects.values("doc_id","candidate_id","c_psimg","c_adhar","c_pan","c_bankDetails","c_bankStatement","c_salarySlips","c_expLetter","c_previousJoiningLetter","c_degree","c_masters","c_HSC","c_SSC","c_otherCertificate","status",))
    return JsonResponse({'data':queryset})




@require_GET
def download_documents(request):
    doc_id = request.GET.get('doc_id')
    onboarding = get_object_or_404(Onboarding, doc_id=doc_id)

    # Create a zip file
    zip_filename = f'documents_{doc_id}.zip'
    zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)

    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        # Add each document to the zip file
        for document_field in Onboarding._meta.get_fields():
            if document_field.name.startswith('c_') and getattr(onboarding, document_field.name):
                document_path = os.path.join(settings.MEDIA_ROOT, str(getattr(onboarding, document_field.name)))
                zip_file.write(document_path, os.path.basename(document_path))

    # Prepare the zip file for download
    response = HttpResponse(open(zip_file_path, 'rb').read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

    # Clean up: Delete the temporary zip file
    os.remove(zip_file_path)

    return response



@login_required(login_url=reverse_lazy('accounts:login'))
def interviews_report(request):
  
    context=(get_session(request))
    request.session.save()

    return render(request, 'hr/reports/InterviewReport.html', context)

def interviewsdata(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(candidateResume.objects.filter(created_at__range = daterange).values("candidate_id","name","phone_number","email","resume","remarks","status","Exp","created_at","department__name","designation__name","interviewFeedback","interviewFeedback_date"))
                    # ("emp_id","candidate_id","name","doj","department__name","designation__name","documents_id","status",))
    return JsonResponse({'data':queryset})

def track_interviewsreport(request):
    trackList = Interview.objects.select_related('candidate_id').order_by('-interviewDate').all()
    context = {
        'trackList': trackList,
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'hr/reports/interviewTrackerReport.html', context)

def track_interviewsdatareport(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange   = [start_date, end_date]
    queryset = list(Interview.objects.filter(interviewDate__range = daterange).values("candidate_id__name","candidate_id__phone_number","candidate_id__email","candidate_id__department__name","candidate_id__designation__name","interviewMode","interviewRound","interviewDate","interviewTime","interviewround_remarks","interviewround_status",))
                    # ("emp_id","candidate_id","name","doj","department__name","designation__name","documents_id","status",))
    return JsonResponse({'data':queryset})


def onboarding_report(request):
    onboardingList = Onboarding.objects.all().order_by('-candidate_id').all()
    context = {
        'onboardingList': onboardingList,
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'hr/reports/onboardingReport.html', context)

def onboardingdata_report(request):
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime(2022, 4, 1)
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.today()

    daterange = [start_date, end_date]
    queryset = candidateResume.objects.filter(
    interviewFeedback='Selected',
    interviewFeedback_date__range=daterange
)
    
    # Filter candidateResume objects where interviewFeedback is 'Selected'
    #queryset = candidateResume.objects.filter(interviewFeedback='Selected',interviewFeedback_date__range = daterange)

    # Example of fetching specific fields
    selected_candidates = list(queryset.values(
    "name",
    "phone_number",
    "email",
    "department__name",
    "designation__name",
    "interviewFeedback",
    "interviewFeedback_date",
))

    return JsonResponse({'data': selected_candidates})
