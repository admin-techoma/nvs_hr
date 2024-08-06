from datetime import date, datetime, timedelta ,date
from decimal import Decimal
import json
import fitz
import os
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q
from django.db.models import Case, Count, IntegerField, Q, Value, When

from django.views.decorators.csrf import csrf_exempt

from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from docx import Document

from core import settings
from employee.views import calculate_paid_leave_days
from employee.models import (Attendance, Department, Designation, Employee,
                             Gender, LeaveApplication, Position,
                             ResignApplication)
from payroll.models import Monthly_salary, Payroll

from hr.forms import (InterviewForm, InterviewFormFields,
                    InterviewSelectionFeedback, NewResumeUploadForm, OnboardingKYCForm, ResumeUploadForm,
                    onboardingAccountDetilsForm, onboardingEducationDetilsForm,
                    professionalDetailsForm, resumeEditForm)
from hr.models import Announcement, Company, CompanyBankDetails, CompanyBranch, CompanyPayrollDetails, HolidayList, HolidayMaster, Interview, Onboarding, Policies,  WeekOff, WeekOffDay, WeekOffNo, candidateResume


import logging
logger = logging.getLogger(__name__)

from django import template
register = template.Library()


def generate_next_emp_id():
    last_employee = Employee.objects.last()
    if last_employee:
        last_emp_id = last_employee.emp_id
        emp_number = int(last_emp_id[5:]) + 1
        return f'NIBPL{str(emp_number).zfill(3)}'
    else:
        return 'NIBPL001'
    
def get_session(request):
    # Retrieve the latest employee from the database
    emp_id = generate_next_emp_id()

    # Rest of your code remains unchanged
    employee_name = request.session.get('employee_name', '')
    department = request.session.get('department', '')
    designation = request.session.get('designation', '')
    documents_id = request.session.get('documents_id', '')
   
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
        'reporting_take': reporting_take,
        'session_email': session_email,
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


def admin_dashboard(request):
    context = get_session(request)
    emp_data = Employee.objects.all()
 
    context.update({
        'emp_data': emp_data,
       
    })
    
    request.session.save()
    return render(request, 'admin/dashboard.html', context)

@login_required(login_url=reverse_lazy('accounts:login'))
def hr_dashboard(request):
    context = get_session(request)
    today = datetime.now()
    employees = Employee.objects.filter(dob__day=today.day, dob__month=today.month)
    emp_active= Employee.objects.filter(status='Active').count()
    today_clock_ins_count = Attendance.count_today_clock_ins()
   
    emp_leave= LeaveApplication.objects.filter(leave_status=1,leave_from_date__lte=today,leave_to_date__gte=today).count() # full leave  + half leave
    interview_panding = candidateResume.objects.filter(
        interviewFeedback='Pending'
    ).exclude(employee__isnull=False).count()

    
    
    employeesdoj = Employee.objects.filter(doj__day=today.day, doj__month=today.month)
    approved_leave_employees = LeaveApplication.objects.filter(
        leave_status=1,  # 'Approved' status
        leave_from_date__lte=today,  # Leave starts before or on today
        leave_to_date__gte=today     # Leave ends after or on today
    ).values_list('employee', flat=True).distinct()
    onLeaveEmp = Employee.objects.filter(emp_id__in=approved_leave_employees)

    interviewlist = candidateResume.objects.all()
    resignlist = ResignApplication.objects.all()
    # In your views or wherever needed
    
    
    context.update({'employees': employees,'employeesdoj':employeesdoj, 'onLeaveEmp':onLeaveEmp,
                    'emp_active':emp_active,
                    'today_clock_ins_count':today_clock_ins_count,'emp_leave':emp_leave,'interview_panding':interview_panding,'interviewlist':interviewlist,'resignlist':resignlist,
                   })
    request.session.save()
    return render(request, 'hr/hrdashboard.html', context)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            existing_candidate = candidateResume.objects.filter(Q(phone_number=phone_number) | Q(email=email))
            if existing_candidate.exists():
                error_message = 'Email or Mobile Already Registered With Us.'
                return JsonResponse({'error': error_message}, status=400)
            else:
                new_resume = form.save()
                return redirect('hr:resume_list')
        else:
            form_errors = form.errors.as_ul()
            return JsonResponse({'errors': form_errors}, status=400)
    else:
        form = ResumeUploadForm()
    return render(request, 'hr/resume_upload.html', {'form': form})

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
def resume_list(request):
    employees = Employee.objects.values_list('candidate_id', flat=True)
    # resumelist = candidateResume.objects.all().order_by('-candidate_id')
    resumelist = candidateResume.objects.exclude(interviewFeedback='IsEmployeeNow').order_by('-candidate_id')
    context = {
        'resumelist': resumelist,
        'statuschoices': candidateResume.status.field.choices,
        'employees': employees,
    }
    context.update(get_session(request))
    request.session.save()
    return render(request, 'hr/Hrresumelist.html', context)


def get_interviewround_list_id_details(request, id):
    try:
        interview = Interview.objects.get(id=id)
        department_choices = list(Department.objects.values('id', 'name'))
        designation_choices = list(Designation.objects.filter(department=interview.department).values('id', 'name'))

        response_data = {
            'id': interview.id,
            # 'candidate_id': interview.candidate_id,
            'interviewDate': interview.interviewDate,
            'interviewTime': interview.interviewTime,
            'interviewRound': interview.interviewRound,
            'interviewMode': interview.interviewMode,
            'interviewer': interview.interviewer,  # Assuming interviewer is stored in the same format
            'interviewround_remarks': interview.interviewround_remarks,
            'interviewround_status': interview.interviewround_status,
            'department': interview.department.id if interview.department else '',
            'designation': interview.designation.id if interview.designation else '',
            'department_choices': department_choices,
            'designation_choices': designation_choices,
            'interviewRoundChoices': [{'value': choice[0], 'display': choice[1]} for choice in Interview._meta.get_field('interviewRound').choices]
        }
        return JsonResponse(response_data, safe=False)
    except Interview.DoesNotExist:
        return JsonResponse({'error': 'Interview round not found'}, status=404)
    
@csrf_exempt
def update_interviewround(request):
    if request.method == 'POST':
        interview_id = request.POST.get('interviewround_id')
        try:
            interview = Interview.objects.get(id=interview_id)
            # interview.candidate_id = request.POST.get('candidate_id')
            interview.interviewDate = request.POST.get('interviewDate')
            interview.interviewTime = request.POST.get('interviewTime')
            interview.interviewRound = request.POST.get('interviewRound')
            interview.interviewMode = request.POST.get('interviewMode')
            interview.interviewer = request.POST.get('interviewer')
            interview.interviewround_remarks = request.POST.get('interviewround_remarks')
            interview.interviewround_status = request.POST.get('interviewround_status')
            interview.department_id = request.POST.get('department')
            interview.designation_id = request.POST.get('designation')
            interview.save()
            return JsonResponse({'success': 'Interview round updated successfully!'})
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview round not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
 


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
# @login_required(login_url=reverse_lazy('accounts:login'))
def convert_pdf_to_html(pdf_file_path):
    try:
        doc = fitz.open(pdf_file_path)
        html_content = "<html><body>"
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("html")
            html_content += text
        html_content += "</body></html>"
        return html_content
    except fitz.FileNotFoundError:
        return JsonResponse({"error": "PDF file not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def convert_docx_to_html(docx_file_path):
    try:
        if not os.path.exists(docx_file_path):
            return JsonResponse({"error": "DOCX file not found"}, status=404)

        doc = Document(docx_file_path)
        html_content = "<html><body>"

        for paragraph in doc.paragraphs:
            html_content += f"<p>{paragraph.text}</p>"

        html_content += "</body></html>"
        return html_content

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def preview_resume(request, resume_id):
    context=(get_session(request))

    try:
        resume = candidateResume.objects.get(pk=resume_id)
        file_path = resume.resume.path  # Access the 'path' attribute on the 'resume' instance
        file_extension = file_path.split(".")[-1].lower()  # Get the file extension
        if file_extension == "pdf":
            # Handle PDF file
            html_content = convert_pdf_to_html(file_path)
            return HttpResponse(html_content, content_type='text/html')

        elif file_extension in ("doc", "docx"):
            # Handle DOC or DOCX file
            html_content = convert_docx_to_html(file_path)
            return HttpResponse(html_content, content_type='text/html')

        return JsonResponse({"error": "Unsupported file format"}, status=400)
    except candidateResume.DoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)
    
#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def edit_resume(request, resume_id):
    if request.method == 'POST':
        # Get the instance of the Resume model
        resume = candidateResume.objects.get(pk=resume_id)
        form = resumeEditForm(request.POST, request.FILES, instance=resume) 
        if form.is_valid():
            form.save()  # This will update the model with the form data
            return redirect('hr:resume_list')  # Redirect to the resume list page or any other page
    else:
        # Handle GET request or display the form
        resume = candidateResume.objects.get(pk=resume_id)
        form = resumeEditForm(instance=resume)  # Replace with the actual form name

    # Render the edit form with the resume data
    context = {'resume': resume, 'form': form, 'statuschoices': candidateResume.status.field.choices}
    return render(request, 'hr/resumeUpdate.html', context)

def update_interview_remarks_view(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        remarks = request.POST.get('remarks')
     
        # Add logic to update the database
        return JsonResponse({'success': True})  # Return a JSON response indicating success
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def schedule_interview(request, candidate_id):
    context = get_session(request)
    sender = context['session_email']
    sender_name = context['employee_name']
    sender_designation = context['designation']
    InterviewFieldsets = InterviewFormFields()
    interviewdepartment = Department.objects.all()
    interviews = Interview.objects.filter(candidate_id=candidate_id)
    resume = get_object_or_404(candidateResume, pk=candidate_id)
    interviewRound = request.POST.get('interviewRound')

    if request.method == 'POST':
        # form = professionalDetailsForm(request.POST, instance=resume)
        interviewFeedbackForm = InterviewSelectionFeedback(request.POST, instance=resume)
        interview_form = InterviewForm(request.POST)

        if interview_form.is_valid():
          
            
            # Save department, designation, and interviewer to the candidateResume instance
            department_id = request.POST.get('department')
            designation_id = request.POST.get('designation')
            interviewMode = request.POST.get('interviewMode')
            interview_remarks = request.POST.get('interviewround_remarks')

            selected_department = Department.objects.get(pk=department_id)
            selected_designation = Designation.objects.get(pk=designation_id)
            resume.department = selected_department
            resume.designation = selected_designation
            resume.save()

            # Save interview details
            interview = interview_form.save(commit=False)
            interview.candidate_id = resume
            interview.interviewer = request.POST.get('interviewer').split('~')[-1] if '~' in request.POST.get('interviewer') else ''
            interview.department = selected_department
            interview.designation = selected_designation
            interview.interviewround_remarks = interview_remarks
            interview.save()

            # Prepare email context and send emails
            interviwer = request.POST.get('interviewer')
          
            interviewDate_obj = request.POST.get('interviewDate')
            interviewTime_obj = request.POST.get('interviewTime')
            designationoption = request.POST.get('hiddendesignationoptions')
            interviewMode = request.POST.get('interviewMode')
            
            interviewDate = datetime.strptime(interviewDate_obj, '%Y-%m-%d').strftime('%d-%m-%Y')
            interviewTime = datetime.strptime(interviewTime_obj, '%H:%M').strftime('%I:%M %p')
            
            if interviewMode == 'Online':
                interviewLinkLocation = request.POST.get('interviewLink')
            else:
                interviewLinkLocation = 'Location: 132-133,Samanvay Saptarshi, Near Monalisha Manjalpur, Vadodara 390011 Gujarat.'

            interviewer_email = interviwer.split('~')[1] if '~' in interviwer else interviwer 
            candidate_email = resume.email
            cc2_email = interviewer_email
            
            email_context = {
                'candidate': resume.name,
                'interviewDate': interviewDate,
                'interviewTime': interviewTime,
                'designationoption': designationoption,
                'interviewLinkLocation': interviewLinkLocation,
                'sender_name': sender_name,
                'sender_designation': sender_designation,
            }

            email_html = render_to_string('email_templates/interiew_email.html', email_context)
            ccemail_html = render_to_string('email_templates/ccemail_interview_reminder.html', email_context)
            send_mail(
                'Techoma Technologies Pvt Ltd: Interview Schedule for {}'.format(interviewRound),
                '',
                sender,
                [candidate_email],
                html_message=email_html
            )

            cc_email = EmailMessage(
                'Techoma Technologies Pvt Ltd: Interview Schedule for {}'.format(interviewRound),
                ccemail_html,
                sender,
                [cc2_email]
            )
            cc_email.content_subtype = "html"
            cc_email.attach(resume.resume.name, resume.resume.read(), 'application/pdf')
            cc_email.send()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                response_data = {
                    'id': interview.id,
                    # 'candidate_id':interview.candidate_id,
                    'interviewDate': interview.interviewDate.strftime('%Y-%m-%d'),
                    'interviewTime': interview.interviewTime.strftime('%H:%M'),
                    'interviewRound': interview.get_interviewRound_display(),
                    'interviewMode': interview.get_interviewMode_display(),
                    'interviewer': interview.interviewer,
                    'status': interview.get_interviewround_status_display(),
                }
                return JsonResponse(response_data)

            messages.success(request, 'Interview has been scheduled successfully.')
            return HttpResponseRedirect(reverse('hr:scheduleInterview', args=[candidate_id]))
        else:
            
            for field, errors in interview_form.errors.items():
                for error in errors:
                    if field != '__all__':
                        messages.error(request, f'{interview_form.fields[field].label}: {error}')
                    else:
                        messages.error(request, f'Interview Form: {error}')
    
    else:
     
        interviewFeedbackForm = InterviewSelectionFeedback(instance=resume)
    
    context.update({
        'resume': resume,
        'InterviewFieldsets': InterviewFieldsets,
        'interviews': interviews,
        'interviewFeedbackForm': interviewFeedbackForm,
        'interviewdepartment': interviewdepartment,
    })
    request.session.save()
    
    return render(request, 'hr/Shortlistedcandidateinterviewschedule.html', context)


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounssssts:login'))
def upload_new_resume(request, candidate_id):
    if request.method == 'POST':
        form = NewResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded resume to the candidateResume model
            resume = candidateResume.objects.get(pk=candidate_id)
            resume.resume = form.cleaned_data['resume']
            resume.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Form validation failed'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def create_interview(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if candidate_id:
            form = InterviewForm(request.POST)
            if form.is_valid():
                interview = form.save(commit=False)
                interview.candidate_id_id = candidate_id  # Set the candidate_id foreign key
                interview.save()
                return JsonResponse({'success': True})
            else:
                errors = form.errors.as_json()
                return JsonResponse({'success': False, 'errors': errors})
        else:
            return JsonResponse({'success': False, 'message': 'Candidate ID is missing'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def save_interview_feedback(request, candidate_id):
    if request.method == 'POST':
        try:
            resume = candidateResume.objects.get(pk=candidate_id)
            interviewFeedbackForm = InterviewSelectionFeedback(request.POST, instance=resume)
            if interviewFeedbackForm.is_valid():
                interviewFeedbackForm.save()
                form = InterviewSelectionFeedback(request.POST, instance=candidateResume.objects.get(pk=candidate_id))
                if form.is_valid():
                    # Retrieve the value of interviewFeedback_date from the form data
                    interviewFeedback_date = form.cleaned_data['interviewFeedback_date']
                    # Save the form and assign the interviewFeedback_date value to the model field
                    instance = form.save(commit=False)
                    instance.interviewFeedback_date = interviewFeedback_date
                    instance.save()

                    return JsonResponse({'success': True, 'message': 'Data saved successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Form validation failed'})
            else:
                return JsonResponse({'success': False, 'message': 'Interview feedback form validation failed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Internal Server Error'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
def onboarding_list(request):
    candidate_resumes = candidateResume.objects.filter(
        interviewFeedback='Selected'
    ).exclude(candidate_id__in=Employee.objects.values_list('candidate_id', flat=True))
    onboarding_status = {}

    for candidate in candidate_resumes:
        onboarding_exists = Onboarding.objects.filter(candidate_id=candidate.candidate_id).exists()
        employee_exists = Employee.objects.filter(candidate_id=candidate.candidate_id).exists()

        onboarding_status[candidate.candidate_id] = {
            'onboarding_exists': onboarding_exists,
            'employee_exists': employee_exists,
        }

    if request.method == 'POST' and 'download_button' in request.POST:
        df = pd.DataFrame(list(candidate_resumes.values()))  # Use values() on the queryset
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="candidate_data.csv"'
        df.to_csv(response, index=False)
        return response
    else:
        context = {
            'onboardinglist': candidate_resumes,
            'onboarding_status': onboarding_status,
        }
        context.update(get_session(request))
        request.session.save()

        return render(request, 'hr/hronboardinglistview.html', context)
    
def get_or_create_onboarding_instance(candidate_id):
    try:
        return Onboarding.objects.get(candidate_id_id=candidate_id)
    except Onboarding.DoesNotExist:
        return Onboarding(candidate_id_id=candidate_id)

def has_kyc_details(onboarding_instance):
    # Check if KYC details are present in the database
    return all([onboarding_instance.c_psimg, onboarding_instance.c_adhar, onboarding_instance.c_pan, onboarding_instance.c_bankDetails])

def has_account_details(onboarding_instance):
    # Check if Accounts details are present in the database
    return all([onboarding_instance.c_bankStatement])



def onboarding_process(request, onboarding_id):
    onboarding_instance = get_or_create_onboarding_instance(onboarding_id)
    onboarding_form = OnboardingKYCForm(instance=onboarding_instance)
    onboarding_AccountDetils_Form = onboardingAccountDetilsForm(instance=onboarding_instance)
    onboarding_EducationDetils_Form = onboardingEducationDetilsForm(instance=onboarding_instance)
    candidate_resume = get_object_or_404(candidateResume, candidate_id=onboarding_instance.candidate_id_id)
    if request.method == 'POST':
        if 'form1_submit' in request.POST:
            onboarding_form = OnboardingKYCForm(request.POST, request.FILES, instance=onboarding_instance)
            if onboarding_form.is_valid():
                onboarding_form.save()
                messages.success(request, 'KYC documents form submitted successfully.')
                return redirect('hr:add_employee', candidate_resume.candidate_id)
            else:
                messages.error(request, 'KYC documents form submission failed. Please check the errors.')
        elif 'form2_submit' in request.POST:
            if has_account_details(onboarding_instance):
                onboarding_EducationDetils_Form = onboardingEducationDetilsForm(request.POST, request.FILES, instance=onboarding_instance)
                if onboarding_EducationDetils_Form.is_valid():
                    onboarding_EducationDetils_Form.save()
                    messages.success(request, 'Educational documents form submitted successfully.')
                else:
                    messages.error(request, 'Educational documents submission failed. Please check the errors.')
            else:
               messages.error(request, 'Please submit Account details first.')
        elif 'form3_submit' in request.POST:
            if has_kyc_details(onboarding_instance):
                onboarding_AccountDetils_Form = onboardingAccountDetilsForm(request.POST, request.FILES, instance=onboarding_instance)
                if onboarding_AccountDetils_Form.is_valid():
                    onboarding_AccountDetils_Form.save()
                    messages.success(request, 'Accounts details form submitted successfully.')
                else:
                    messages.error(request, 'Accounts details form submission failed. Please check the errors.')
            else:
                messages.error(request, 'Please submit KYC documents first.')

    context = {
        'onboarding_form': onboarding_form,
        'onboarding_AccountDetils_Form': onboarding_AccountDetils_Form,
        'onboarding_id': onboarding_id,
        'onboarding_EducationDetils_Form': onboarding_EducationDetils_Form,
        'candidate_resume':candidate_resume,
    }

    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render(request, 'hr/hronboardingfileupload.html', context)

def get_or_create_onboarding_instance(candidate_id):
    try:
        return Onboarding.objects.get(candidate_id_id=candidate_id)
    except Onboarding.DoesNotExist:
        return Onboarding(candidate_id_id=candidate_id)


def view_documents(request,candidate_id):
    onboarding_documents = Onboarding.objects.filter(candidate_id=candidate_id)
    context={
        'onboarding_documents':onboarding_documents,
    }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()

    return render(request, 'hr/view_documents.html', context)

def updateimg(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_psimg' in request.FILES:
                if onboarding_instance.c_psimg:
                    # Delete previous image if exists
                    onboarding_instance.c_psimg.delete()
                onboarding_instance.c_psimg = request.FILES['c_psimg']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_psimg uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

def updateaadhar(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_adhar' in request.FILES:
                if onboarding_instance.c_adhar:
                    # Delete previous image if exists
                    onboarding_instance.c_adhar.delete()
                onboarding_instance.c_adhar = request.FILES['c_adhar']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_adhar uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def updatepan(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_pan' in request.FILES:
                if onboarding_instance.c_pan:
                    # Delete previous image if exists
                    onboarding_instance.c_pan.delete()
                onboarding_instance.c_pan = request.FILES['c_pan']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_pan uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatebankdetails(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_bankDetails' in request.FILES:
                if onboarding_instance.c_bankDetails:
                    # Delete previous image if exists
                    onboarding_instance.c_bankDetails.delete()
                onboarding_instance.c_bankDetails = request.FILES['c_bankDetails']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_bankDetails uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def updatebankstatement(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_bankStatement' in request.FILES:
                if onboarding_instance.c_bankStatement:
                    # Delete previous image if exists
                    onboarding_instance.c_bankStatement.delete()
                onboarding_instance.c_bankStatement = request.FILES['c_bankStatement']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_bankStatement uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatesalaryslips(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_salarySlips' in request.FILES:
                if onboarding_instance.c_salarySlips:
                    # Delete previous image if exists
                    onboarding_instance.c_salarySlips.delete()
                onboarding_instance.c_salarySlips = request.FILES['c_salarySlips']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_salarySlips uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def skipsalaryslips(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_salarySlips' in request.FILES:
                if onboarding_instance.c_salarySlips:
                    # Delete previous image if exists
                    onboarding_instance.c_salarySlips.delete()
                onboarding_instance.c_salarySlips = request.FILES['c_salarySlips']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_salarySlips uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



def updateexpletter(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_expLetter' in request.FILES:
                if onboarding_instance.c_expLetter:
                    # Delete previous image if exists
                    onboarding_instance.c_expLetter.delete()
                onboarding_instance.c_expLetter = request.FILES['c_expLetter']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_expLetter uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatepreviousjoiningletter(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_previousJoiningLetter' in request.FILES:
                if onboarding_instance.c_previousJoiningLetter:
                    # Delete previous image if exists
                    onboarding_instance.c_previousJoiningLetter.delete()
                onboarding_instance.c_previousJoiningLetter = request.FILES['c_previousJoiningLetter']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_previousJoiningLetter uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatec_degree(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_degree' in request.FILES:
                if onboarding_instance.c_degree:
                    # Delete previous image if exists
                    onboarding_instance.c_degree.delete()
                onboarding_instance.c_degree = request.FILES['c_degree']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_degree uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatemasters(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_masters' in request.FILES:
                if onboarding_instance.c_masters:
                    # Delete previous image if exists
                    onboarding_instance.c_masters.delete()
                onboarding_instance.c_masters = request.FILES['c_masters']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_masters uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatehsc(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_HSC' in request.FILES:
                if onboarding_instance.c_HSC:
                    # Delete previous image if exists
                    onboarding_instance.c_HSC.delete()
                onboarding_instance.c_HSC = request.FILES['c_HSC']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_HSC uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updatessc(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_SSC' in request.FILES:
                if onboarding_instance.c_SSC:
                    # Delete previous image if exists
                    onboarding_instance.c_SSC.delete()
                onboarding_instance.c_SSC = request.FILES['c_SSC']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_SSC uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def updateothercertificate(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = Onboarding.objects.get(pk=pk)
            if 'c_otherCertificate' in request.FILES:
                if onboarding_instance.c_otherCertificate:
                    # Delete previous image if exists
                    onboarding_instance.c_otherCertificate.delete()
                onboarding_instance.c_otherCertificate = request.FILES['c_otherCertificate']
                onboarding_instance.save()
                return JsonResponse({'message': 'c_otherCertificate uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



def updateresume(request,pk):
    
    if request.method == 'POST':
        try:
            onboarding_instance = candidateResume.objects.get(pk=pk)
            if 'resume' in request.FILES:
                if onboarding_instance.resume:
                    # Delete previous image if exists
                    onboarding_instance.resume.delete()
                onboarding_instance.resume = request.FILES['resume']
                onboarding_instance.save()
                return JsonResponse({'message': 'resume uploaded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'No file found'}, status=400)
        except Onboarding.DoesNotExist:
            return JsonResponse({'error': 'Onboarding instance does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def load_designation(request):
    department_id = request.GET.get('department')
    designations = Designation.objects.filter(department_id=department_id).order_by('name')
    
    designation_options = [{'id': designation.id, 'name': designation.name} for designation in designations]

    return JsonResponse({'designations': designation_options})




#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def ajax_load_reporting_managers(request):
    
    department_id = request.GET.get('department_id')

    # Get reporting managers from the specified department and admin department where reporting_take is true
    reporting_managers = Employee.objects.filter(
        Q(department_id=department_id, reporting_take=True) | 
        Q(department__name='Admin', reporting_take=True)
    ).values('emp_id', 'name')

    return JsonResponse({'reporting_managers': list(reporting_managers)})


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))

def ajax_load_interviewer(request):
    interview_round = request.GET.get('interview_round')
    department_id = request.GET.get('department_id')
    
    hr_department = Department.objects.get(name='HR')
    admin_department = Department.objects.get(name='Admin')

    if interview_round == 'HR Round':
        interviewers = Employee.objects.filter(department=hr_department).values('emp_id', 'emp_user__email', 'first_name')
    else:
        interviewers = Employee.objects.filter(
            Q(department_id=department_id) | 
            Q(department=hr_department) | 
            Q(department=admin_department)
        ).values('emp_id', 'emp_user__email', 'first_name')

    return JsonResponse({'interviewers': list(interviewers)})

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def view_employee(request):
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
    
    emp_data = Employee.objects.all()
    
    for employee in emp_data:
        employee.doj = employee.doj.strftime('%Y-%m-%d')
        
    onboarding_exists = Onboarding.objects.all()
    
    payroll_status = "Active"  # Replace this with the actual payroll status logic
    if request.method == 'POST' and 'download_button' in request.POST:
        df = pd.DataFrame(list(emp_data.values()))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employee_report.csv"'
        df.to_csv(response, index=False)
        return response
    else:
        context = {
            'emp_data': emp_data,
            'payroll_status': payroll_status,
            'onboarding_exists':onboarding_exists,
            'daterange':daterange
            
            
        }

        context.update(get_session(request))  # Call get_session to retrieve the dictionary
        request.session.save()

    return render(request, 'hr/Employeelist.html', context)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def view_attendance(request):
    employee_data = Employee.objects.all()
    today = date.today()
    current_month = today.month
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today
    current_year = timezone.now().year

    active_employee_count = Employee.objects.filter(status='Active').count()

    leave_data = LeaveApplication.objects.filter(leave_status=1).select_related('employee').all()
    employees_on_leave_today = LeaveApplication.objects.filter(
        leave_from_date__lte=today,
        leave_to_date__gte=today,
        leave_status=1 
    ).count()

    # Filter Attendance objects for the current month
    attendances_current_month = Attendance.objects.filter(
        date__year=current_year,
        date__month=current_month
    )

    # Annotate each employee with the count of full day attendances
    employees_with_attendance_counts = Employee.objects.annotate(
        full_day_count=Count(
            Case(
                When(attendance__date__year=current_year,
                     attendance__date__month=current_month,
                     attendance__is_full_day=True,
                     then=Value(1)),
                output_field=IntegerField(),
            )
        ),
        half_day_count=Count(
            Case(
                When(attendance__date__year=current_year,
                     attendance__date__month=current_month,
                     attendance__is_half_day=True,
                     then=Value(1)),
                output_field=IntegerField(),
            )
        ),
        absent_day_count=Count(
        Case(
            When(attendance__date__year=current_year,
                 attendance__date__month=current_month,
                 attendance__is_absent=True,
                 then=Value(1)),
            output_field=IntegerField(),
            )
        )
    )

    total_paid_leaves_list = []
    for employee in employee_data:
        leaves = LeaveApplication.objects.filter(
            Q(employee=employee),
            Q(leave_from_date__year=current_year, leave_from_date__month=current_month) |
            Q(leave_to_date__year=current_year, leave_to_date__month=current_month)
        )
        paid_leaves = leaves.filter(leave_status=1)
        total_paid_leaves = 0
        for leave in paid_leaves:
            leave_from_datetime = datetime.combine(leave.leave_from_date, leave.leave_from_time)
            leave_to_datetime = datetime.combine(leave.leave_to_date, leave.leave_to_time)
            leave_total = calculate_paid_leave_days(leave, current_month, current_year)
            total_paid_leaves += leave_total
            
        total_paid_leaves_list.append(total_paid_leaves)
    attendance_report = {
        'Employee_ID': [emp.emp_id for emp in employee_data],
        'Employee_Name': [emp.name for emp in employee_data],
        'Present': [emp.full_day_count for emp in employees_with_attendance_counts],
        'Half Day': [emp.half_day_count for emp in employees_with_attendance_counts],
        'Absent': [emp.absent_day_count for emp in employees_with_attendance_counts],
        'Leave': total_paid_leaves_list,
    }

    current_date = first_day_of_month
    while current_date <= last_day_of_month:
        attendance_report[current_date.strftime('%d-%m-%Y')] = []
        for emp_id in attendance_report['Employee_ID']:
            employee = Employee.objects.get(emp_id=emp_id)
            attendance_obj = Attendance.objects.filter(employee=employee, date=current_date).first()
            leave_obj = LeaveApplication.objects.filter(
                Q(employee=employee),
                Q(leave_from_date__lte=current_date, leave_to_date__gte=current_date),
                leave_status=1
            ).first()
            if leave_obj:
                leave_from_datetime = leave_obj.leave_from_date + timedelta(hours=leave_obj.leave_from_time.hour)
                leave_to_datetime = leave_obj.leave_to_date + timedelta(hours=leave_obj.leave_to_time.hour)

                if current_date == leave_from_datetime and leave_obj.leave_from_time.hour == 18:
                    # Check if clock-in and clock-out times exist in Attendance
                    attendance_obj = Attendance.objects.filter(employee=employee, date=current_date).first()
                    if attendance_obj and attendance_obj.clock_in and attendance_obj.clock_out:
                        clock_in_time = attendance_obj.clock_in.strftime('%H:%M')
                        clock_out_time = attendance_obj.clock_out.strftime('%H:%M')
                        attendance_report[current_date.strftime('%d-%m-%Y')].append(f"{clock_in_time}-{clock_out_time}")
                    else:
                        attendance_report[current_date.strftime('%d-%m-%Y')].append("Half Day Leave")
                elif current_date == leave_to_datetime and leave_obj.leave_to_time.hour == 9:
                    # Check if clock-in and clock-out times exist in Attendance
                    attendance_obj = Attendance.objects.filter(employee=employee, date=current_date).first()
                    if attendance_obj and attendance_obj.clock_in and attendance_obj.clock_out:
                        clock_in_time = attendance_obj.clock_in.strftime('%H:%M')
                        clock_out_time = attendance_obj.clock_out.strftime('%H:%M')
                        attendance_report[current_date.strftime('%d-%m-%Y')].append(f"{clock_in_time}-{clock_out_time}")
                    else:
                        attendance_report[current_date.strftime('%d-%m-%Y')].append("Half Day Leave")
                elif leave_from_datetime < current_date < leave_to_datetime:
                    attendance_report[current_date.strftime('%d-%m-%Y')].append(leave_obj.leave_type)
                else:
                    attendance_report[current_date.strftime('%d-%m-%Y')].append(leave_obj.leave_type)
            elif attendance_obj:
                if attendance_obj.is_absent:
                    attendance_report[current_date.strftime('%d-%m-%Y')].append("Absent")
                else:
                    clock_in_time = attendance_obj.clock_in.strftime('%H:%M') if attendance_obj.clock_in else ""
                    clock_out_time = attendance_obj.clock_out.strftime('%H:%M') if attendance_obj.clock_out else ""
                    attendance_report[current_date.strftime('%d-%m-%Y')].append(f"{clock_in_time}-{clock_out_time}")
            else:
                attendance_report[current_date.strftime('%d-%m-%Y')].append(0)
        current_date += timedelta(days=1)

    if request.method == 'POST' and 'download_button' in request.POST:
        df = pd.DataFrame(attendance_report)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        df.to_csv(response, index=False)
        return response

    context = {
        'employee_data': employee_data,
        'active_employee_count': active_employee_count,
        'employees_on_leave_today': employees_on_leave_today,
    }

    context.update(get_session(request))
    request.session.save()
    return render(request, 'hr/Viewattendancereports.html', context)

@login_required(login_url=reverse_lazy('accounts:login'))
def attendance_report(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    leavedata = LeaveApplication.objects.filter(employee = employee)
    context = {'leavedata':leavedata, "employee":employee}

    context.update(get_session(request))
    request.session.save()
    return render(request, 'hr/reports/attendanceReportcalander.html', context)

def ajax_load_PunchIn_PunchOut(request, emp_id, selectedDate):
    try:
        parsed_date = datetime.strptime(selectedDate, '%d-%m-%Y')

        # Query the Attendance model based on emp_id and parsed date
        attendance = Attendance.objects.get(employee__emp_id=emp_id, date=parsed_date)

        # Extract clock_in and clock_out times from the attendance object
        clock_in = attendance.clock_in.strftime('%H:%M') if attendance.clock_in else None
        clock_out = attendance.clock_out.strftime('%H:%M') if attendance.clock_out else None

        data = {
            'clock_in': clock_in,
            'clock_out': clock_out
        }
        return JsonResponse(data)
    except Attendance.DoesNotExist:
        # Check if selectedDate falls within any leave application date range
        leave_application = LeaveApplication.objects.filter(
            employee__emp_id=emp_id,
            leave_from_date__lte=parsed_date,
            leave_to_date__gte=parsed_date,
            leave_status=1  # Assuming leave_status 1 means approved leave
        ).exists()

        if leave_application:
            return JsonResponse({'error': 'Leave application exists for the selected date'}, status=409)
        else:
            return JsonResponse({'error': 'Attendance data not found'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def ajax_save_attendance(request, emp_id, selectedDate):
    if request.method == 'POST':
        punch_in = request.POST.get('punch_in')
        punch_out = request.POST.get('punch_out')
        try:
            punch_in_time = datetime.strptime(punch_in, '%H:%M').time()
            punch_out_time = datetime.strptime(punch_out, '%H:%M').time()
            employee = Employee.objects.get(emp_id=emp_id)
            parsed_date = datetime.strptime(selectedDate, '%Y-%m-%d').date()

            if parsed_date > date.today():
                return JsonResponse({'error': 'Future dates cannot be modified'}, status=400)

            if parsed_date.weekday() == 6:
                return JsonResponse({'error': 'Attendance cannot be modified for Sundays'}, status=400)
                
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=parsed_date
            )
            attendance.clock_in = punch_in_time
            attendance.clock_out = punch_out_time
            attendance.save()
            
            return JsonResponse({'success': 'Attendance saved successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def add_employee(request, pk):
    # Fetch data from the database
    department_all = Department.objects.all()
    positions = Position.objects.all()
    genders = Gender.objects.all()
    employees = Employee.objects.all()
    company_branches = CompanyBranch.objects.all()
    holiday_masters = HolidayMaster.objects.all()
    weekoffs = WeekOff.objects.all()

    try:
        candidate = candidateResume.objects.get(candidate_id=pk)
        documents = Onboarding.objects.get(candidate_id=pk)
        candidate_documents = Onboarding.objects.get(candidate_id=candidate.candidate_id)
        candidate_c_psimg = candidate_documents.c_psimg
    except candidateResume.DoesNotExist:
        candidate = None
        documents = None
        candidate_documents = None
        candidate_c_psimg = None

    emp_id = generate_next_emp_id()

    # Calculate the next payroll_id
    last_payroll = Payroll.objects.last()
    if (last_payroll):
        last_payroll_id = last_payroll.payroll_id
        payroll_number = int(last_payroll_id[7:]) + 1
        payroll_id = f'PAYROLL{str(payroll_number).zfill(3)}'
    else:
        payroll_id = 'PAYROLL001'

    if request.method == 'POST':
        # Extract data from the request
        emp_id = request.POST.get("emp_id")
        candidate_id = candidate.candidate_id if candidate else None
        name = request.POST.get("name")
        email = request.POST.get("email")

        # Check if the email already exists
        if (Employee.objects.filter(email=email).exists()):
            messages.info(request, 'Email Id Already Exist.')
            return redirect('hr:add_employee', pk=pk)

        office_email = request.POST.get("office_email")
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        state = request.POST.get("state")
        city = request.POST.get("city")
        country = request.POST.get("country")
        pin_code = request.POST.get("pin_code")
        c_address = request.POST.get("c_address")
        c_state = request.POST.get("c_state")
        c_city = request.POST.get("c_city")
        c_country = request.POST.get("c_country")
        c_pin_code = request.POST.get("c_pin_code")
        contact_no = request.POST.get("contact_no")
        other_contact_no= Decimal(request.POST.get("other_contact_no")) if request.POST.get("other_contact_no") else None
        emergency_contactname = request.POST.get("emergency_contactname")
        emergency_contactnumber = request.POST.get("emergency_contactnumber")
        emergency_relationas = request.POST.get("emergency_relationas")
        # Check if the contact_no already exists
        if (Employee.objects.filter(contact_no=contact_no).exists()):
            messages.info(request, 'contact_no Already Exist.')
            return redirect('hr:add_employee', pk=pk)
        
        
        dob = request.POST.get("dob")
        doj = request.POST.get("doj")
        pf_joining_date = request.POST.get("pf_joining_date", None)
        esic_joining_date = request.POST.get("esic_joining_date", None)

        try:
            dob_date = parse_date(dob)
            doj_date = parse_date(doj)
            pf_joining_date = parse_date(pf_joining_date) if pf_joining_date and pf_joining_date.strip() else None
            esic_joining_date = parse_date(esic_joining_date) if esic_joining_date and esic_joining_date.strip() else None
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

        pfno = request.POST.get("pfno")
        esicno = request.POST.get("esicno", None)
        uanno = request.POST.get("uanno")
        pancard_no = request.POST.get("pancard_no")
        aadhaarcard_no = request.POST.get("aadhaarcard_no")
        account_no = request.POST.get("account_no")
        bank_name = request.POST.get("bank_name")
        ifsc_code = request.POST.get("ifsc_code")
        branch = request.POST.get("branch")
        
        reporting_take = request.POST.get("reporting_take") == 'true'
       

        reporting_to_id = request.POST.get('reporting_to')
        reporting_to = Employee.objects.get(pk=reporting_to_id) if reporting_to_id else None

        department_id = request.POST.get("department")
        selectdepartment = Department.objects.get(pk=department_id)

        holiday_master_id = request.POST.get("holiday_master")
        selectholiday_master = HolidayMaster.objects.get(pk=holiday_master_id)

        company_branch_id = request.POST.get("company_branch")
        selected_company_branch = CompanyBranch.objects.get(id=company_branch_id)

        designation_id = request.POST.get("designation")
        designation = Designation.objects.get(pk=designation_id)

        holidaylist_id = request.POST.get("holidaylist")
        try:
            holidaylist = HolidayList.objects.get(id=holidaylist_id)
        except HolidayList.DoesNotExist:
            holidaylist = None

        position_id = request.POST.get("position")
        selected_position = Position.objects.get(pk=position_id)

        gender_id = request.POST.get("gender")
        selected_gender = Gender.objects.get(pk=gender_id)

        
        # Create employee instance
        employee_instance = Employee.objects.create(
            candidate_id=candidate, emp_id=emp_id, name=name,
            first_name=first_name, middle_name=middle_name, last_name=last_name, email=email, office_email=office_email,
            address=address, state=state, city=city, country=country, pin_code=pin_code,
            c_address=c_address, c_state=c_state, c_city=c_city, c_country=c_country, c_pin_code=c_pin_code,
            contact_no=contact_no,dob=dob, doj=doj, pfno=pfno, esicno=esicno, pf_joining_date=pf_joining_date, esic_joining_date=esic_joining_date,
            uanno=uanno, pancard_no=pancard_no, aadhaarcard_no=aadhaarcard_no, account_no=account_no, bank_name=bank_name, ifsc_code=ifsc_code,
            branch=branch, reporting_take=reporting_take, company_branch=selected_company_branch, department=selectdepartment,
            designation=designation, reporting_to=reporting_to, documents_id=documents, position=selected_position, gender=selected_gender,
            holiday_master=selectholiday_master,emergency_contactname = emergency_contactname,emergency_contactnumber = emergency_contactnumber,emergency_relationas = emergency_relationas
        )

        # Create payroll entry
        Payroll.objects.create(
            payroll_id=payroll_id,
            emp_id=employee_instance
        )

        # Update candidateResume to "IsEmployeeNow"
        if candidate:
            candidate.interviewFeedback = "IsEmployeeNow"
            candidate.save()

        messages.success(request, 'Employee created successfully!')
        return redirect('hr:view_employee')

    context = {
        'emp_id': emp_id,
        'emp': employees,
        'candidate': candidate,
        'department_all': department_all,
        'candidate_c_psimg': candidate_c_psimg,
        'documents': documents,
        'positions': positions,
        'genders': genders,
        'company_branches': company_branches,
        'holiday_masters': holiday_masters,
        'weekoffs': weekoffs,
    }

    context.update(get_session(request))
    request.session.save()

    return render(request, 'hr/hrcreateemployeegenetetionform.html', context)

def update_personal_info(request, id):
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        gender_id = request.POST.get("gender")
        married_status = request.POST.get('married_status')
          
        pancard_no = request.POST.get('pancard_no')
        aadhaarcard_no = request.POST.get('aadhaarcard_no')
        blood_group = request.POST.get('blood_group')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')
        other_contact_no = request.POST.get('other_contact_no')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pin_code = request.POST.get('pin_code')
        c_address = request.POST.get('c_address')
        c_city = request.POST.get('c_city')
        c_state = request.POST.get('c_state')
        c_country = request.POST.get('c_country')
        c_pin_code = request.POST.get('c_pin_code')
        linkedin_profile = request.POST.get('linkedin_profile')
        instagram_profile = request.POST.get('instagram_profile')
        facebook_profile = request.POST.get('facebook_profile')
        emergency_contactname = request.POST.get("emergency_contactname")
        emergency_contactnumber = request.POST.get("emergency_contactnumber")
        emergency_relationas = request.POST.get("emergency_relationas")

        emp_data = Employee.objects.get(emp_id=id)
        emp_data.first_name = first_name
        emp_data.middle_name = middle_name
        emp_data.last_name = last_name
        emp_data.name = name
        emp_data.dob = dob
        if gender_id:
            try:
                emp_data.gender = Gender.objects.get(pk=gender_id)
            except Gender.DoesNotExist:
                # Handle the case when the Gender with the specified ID does not exist
                pass
        emp_data.married_status = married_status
        
        emp_data.pancard_no = pancard_no
        emp_data.aadhaarcard_no = aadhaarcard_no
        emp_data.blood_group = blood_group
        emp_data.email = email
        emp_data.contact_no = contact_no
        emp_data.other_contact_no = other_contact_no
        emp_data.address = address
        emp_data.city = city
        emp_data.state = state
        emp_data.country = country
        emp_data.pin_code = pin_code
        emp_data.c_address = c_address
        emp_data.c_city = c_city
        emp_data.c_state = c_state
        emp_data.c_country = c_country
        emp_data.c_pin_code = c_pin_code
        emp_data.linkedin_profile = linkedin_profile
        emp_data.instagram_profile =instagram_profile
        emp_data.facebook_profile = facebook_profile
        emp_data.emergency_contactname = emergency_contactname
        emp_data.emergency_contactnumber = emergency_contactnumber
        emp_data.emergency_relationas = emergency_relationas
            
        emp_data.save()
        messages.success(request, 'Employee  Update successfully.')
        return redirect('hr:employee_profile', id=id)
    else:
        
        # Handle GET request or other cases
       pass
        

def update_work_info(request, id):
    if request.method == 'POST':
        doj = request.POST.get('doj')
        office_email = request.POST.get('office_email')
        doe = request.POST.get('doe')
        uanno = request.POST.get('uanno')
        pfno = request.POST.get('pfno')
        pf_joining_date = request.POST.get('pf_joining_date')
        pf_exit_date = request.POST.get('pf_exit_date')
        esicno = request.POST.get('esicno')
        esic_joining_date = request.POST.get('esic_joining_date')
        esic_exit_date = request.POST.get('esic_exit_date')

        emp_data = Employee.objects.get(emp_id=id)

        # Validate and parse date inputs
        try:
            if doj:
                emp_data.doj = parse_date(doj)
            if doe:
                emp_data.doe = parse_date(doe)
            if pf_joining_date:
                emp_data.pf_joining_date = parse_date(pf_joining_date)
            if pf_exit_date:
                emp_data.pf_exit_date = parse_date(pf_exit_date)
            if esic_joining_date:
                emp_data.esic_joining_date = parse_date(esic_joining_date)
            if esic_exit_date:
                emp_data.esic_exit_date = parse_date(esic_exit_date)
        except ValidationError:
            # Handle invalid date format error
            messages.error(request, 'Invalid date format. Date must be in YYYY-MM-DD format.')
            return redirect('hr:employee_profile', id=id)

        emp_data.office_email = office_email
        emp_data.uanno = uanno
        emp_data.pfno = pfno
        emp_data.esicno = esicno

        department_id = request.POST.get("workdepartment")
        if department_id:
            try:
                emp_data.department = Department.objects.get(pk=department_id)
            except Department.DoesNotExist:
                pass

        designation_id = request.POST.get("designation")
        if designation_id:
            try:
                emp_data.designation = Designation.objects.get(pk=designation_id)
            except Designation.DoesNotExist:
                pass

        position_id = request.POST.get("position")
        if position_id:
            try:
                emp_data.position = Position.objects.get(pk=position_id)
            except Position.DoesNotExist:
                pass

        company_branch_id = request.POST.get("company_branch")
        if company_branch_id:
            try:
                emp_data.company_branch = CompanyBranch.objects.get(pk=company_branch_id)
            except CompanyBranch.DoesNotExist:
                pass

        emp_data.save()
        messages.success(request, 'Employee work updated successfully.')
        return redirect('hr:employee_profile', id=id)
    else:
        # Handle GET request or other cases
        pass



def update_team_info(request, id):
    
    if request.method == 'POST':
        
            reporting_to = request.POST.get('reporting_to')
            
            emp_data = Employee.objects.get(emp_id=id)
            # emp_data.reporting_to = reporting_to

            department_id = request.POST.get("workdepartment")
            # emp_data.department = Department.objects.get(pk=department_id)
            if department_id:
                try:
                    emp_data.department = Department.objects.get(pk=department_id)
                except Department.DoesNotExist:
                    # Handle the case when the Gender with the specified ID does not exist
                    pass



            reporting_to_id = request.POST.get("reporting_to")
            # emp_data.reporting_to = Employee.objects.get(pk=(reporting_to_id))
            if reporting_to_id:
                try:
                    emp_data.reporting_to = Employee.objects.get(pk=reporting_to_id)
                except Employee.DoesNotExist:
                    # Handle the case when the Gender with the specified ID does not exist
                    pass

           
            emp_data.save()
            messages.success(request, 'Employee  Reporting Update successfully.')
            return redirect('hr:employee_profile', id=id)
    else:
        # Handle GET request or other cases
       pass


def update_payroll_info(request, id):
    emp_data = get_object_or_404(Employee, emp_id=id)
    payrollemp, created = Payroll.objects.get_or_create(emp_id=emp_data)
    
    if request.method == 'POST':
        office_email = request.POST.get('office_email')
        if not office_email:
            return HttpResponse("Office Email is required", status=400)
        
        # Update Payroll data
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

        if not emp_data.emp_user:
            # Create or update User object
            user, created = User.objects.get_or_create(username=emp_data.emp_id)
            user.email = office_email
            user.first_name = emp_data.name
            password = User.objects.make_random_password(length=8)
            user.set_password(password)
            user.save()

            # Update Employee data
            emp_data.status = "Active"
            emp_data.office_email = office_email
            emp_data.emp_user = user
            emp_data.save()
            
            # Send email to the employee with username and password
            subject = 'Employee Portal Access Credentials Verification'
            message = f"""Dear {emp_data.name},

            We trust this email finds you well. We would like to inform you that your details have been successfully verified, and we are pleased to provide you with the login credentials for accessing the Employee Portal.

            Here are your login details:
            Office Email ID: {emp_data.office_email}
            URL : http://peoplepulse.buybestpolicy.in
            Username: {emp_data.emp_id}
            Password: {password}

            Please ensure the confidentiality of your login credentials and do not share them with anyone. If you have any concerns or questions regarding the login process, feel free to reach out to our HR department.

            Thank you for your cooperation, and we hope you find the Employee Portal a valuable resource for your work-related activities.

            Best Regards,
            Techoma Technologies Pvt. Ltd.
            Human Resources Department."""
                    
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [emp_data.email]
            try:
                send_mail(subject, message, email_from, recipient_list)
                logger.info(f"Email sent successfully to {', '.join(recipient_list)}")
            except Exception as e:
                logger.error(f"Error sending email to {', '.join(recipient_list)}: {e}")

        messages.success(request, 'Employee Payroll updated successfully. Employee is Active Now!')
        return redirect('hr:employee_profile', id=id)
    else:
        # Handle GET request or other cases
        pass


def update_bank_info(request, id):
    # emp_data, created = Employee.objects.get_or_create(emp_id=id)
    
    if request.method == 'POST':
        
           
            # emp_data.reporting_to = reporting_to
            account_no = request.POST.get('account_no')
            bank_name = request.POST.get('bank_name')
            ifsc_code = request.POST.get('ifsc_code')
            branch = request.POST.get('branch')
           
            emp_data = Employee.objects.get(emp_id=id)
            
            emp_data.account_no = account_no
            emp_data.bank_name = bank_name
            emp_data.ifsc_code = ifsc_code
            emp_data.branch = branch
           
            emp_data.save()
            messages.success(request, 'Employee  Bank Update successfully.')
            return redirect('hr:employee_profile', id=id)
    else:
        # Handle GET request or other cases
       pass


def update_permission_info(request, id):
    emp_data, created = Employee.objects.get_or_create(emp_id=id)
    
    if request.method == 'POST':

        if 'reporting_take' in request.POST:
            emp_data.reporting_take = True
        else:
            emp_data.reporting_take = False
           
        emp_data.save()
        messages.success(request, 'Employee Permissions Updated successfully.')
        return redirect('hr:employee_profile', id=id)
    else:
        # Handle GET request or other cases
        pass



def check_email_exists(request):
    email = request.GET.get('email', None)
    
    candidate_exists = candidateResume.objects.filter(email=email).exists()
    
    if not email:
        return JsonResponse({'error': 'Email parameter is missing'}, status=400)
    
    # Check if email already exists in the Employee model
    exists = Employee.objects.filter(email=email).exists()
    
    return JsonResponse({'exists': exists,'candidate_exists':candidate_exists})

def check_contact_no_exists(request):
    contact_no = request.GET.get('contact_no', None)
    phone_number = request.GET.get('phone_number', None)
    print("contact_no",contact_no)
    if contact_no:
        exists = Employee.objects.filter(contact_no=contact_no).exists()
        return JsonResponse({'exists': exists})
    
    else:
        phone_number_exists = candidateResume.objects.filter(phone_number=phone_number).exists()
        return JsonResponse({'phone_number_exists': phone_number_exists})



@register.filter
def days_difference(end_date, start_date):
    if end_date and start_date:
        delta = end_date - start_date
        return delta.days
    return 0


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def employee_profile(request, id):
    emp_data = Employee.objects.get(emp_id=id)
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

    try:
        payroll_data = Payroll.objects.get(emp_id=emp_data)
    except Payroll.DoesNotExist:
        payroll_data = None
        
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
    
    employee_regularization = Attendance.objects.filter(
            regularization_requested=True
            ).order_by('id')

    context = {'emp_data': emp_data, 
               'attendances':attendances,
               'employee_regularization':employee_regularization,
               'onboarding_documents': onboarding_documents,
               'total_absents': total_absents,
               'total_presents':total_presents,
               'leavedata': leavedata,
               'payroll_data':payroll_data,
               'all_monthly_salaries': all_monthly_salaries,
               'resign_data':resign_data,
               'employees_reporting_to_selected_manager': employees_reporting_to_selected_manager,
               'emp':emp,'department_all': department_all,'designation':designation,'gender':gender,'position_all':position_all,'company_branch':company_branch,
                'bank_details': {
                'account_no': emp_data.account_no,
                'bank_name': emp_data.bank_name,
                'ifsc_code': emp_data.ifsc_code,
                'branch': emp_data.branch,
                
            }
        }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'employee/employeeprofile.html', context)


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def ajax_newdepartment(request):
   
    
    newdepartment = request.GET.get('newdepartment')
    
    if Department.objects.filter(name=newdepartment).exists():
        return JsonResponse({"valid":False}, status = 200)

    try:
        Department.objects.create(name=newdepartment)
    
        return JsonResponse({"valid":True, "newdepartment":newdepartment}, status = 200)
    
    except Exception as e:

        return JsonResponse({"msg": str(e)}, status=400)


#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def ajax_adddesignation(request):

    designationid = Designation.objects.last()
    if designationid:
        adddesignationno=str(int(designationid.pk) + 1)
    else:
        adddesignationno='26204'
    
    adddepartmentname = request.GET.get('adddepartmentname')
    adddesignation = request.GET.get('adddesignation')
    
    if Designation.objects.filter(name=adddesignation).exists():
        return JsonResponse({"valid":False}, status = 200)

    try:
        
        department_instance = Department.objects.get(name=adddepartmentname)
        Designation.objects.create(department=department_instance, name=adddesignation)


        return JsonResponse({
            "valid": True,
            "adddepartmentname": adddepartmentname,
            "adddesignation": adddesignation,
            'adddesignationno': adddesignationno
        }, status=200)

    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=400)

def direct_employee(request, pk=None):

    department_all = Department.objects.all()
    company_branch = CompanyBranch.objects.all()
    position = Position.objects.all()
    gender = Gender.objects.all()
    emp = Employee.objects.all()
    
    # Initialize variables to None
    candidate = None
    documents = None
    candidate_c_psimg = None
    
    # Check if pk is provided
    if pk:
        try:
            # Retrieve candidate and documents instances
            candidate = candidateResume.objects.get(candidate_id=pk)
            documents = Onboarding.objects.get(candidate_id=pk)
            candidate_c_psimg = documents.c_psimg.url if documents.c_psimg else 'static/admin/img/avtar.jpg'
        except (candidateResume.DoesNotExist, Onboarding.DoesNotExist):
            raise Http404("Candidate or documents not found")

    emp_id = generate_next_emp_id()

    # Calculate the next payroll_id
    last_payroll = Payroll.objects.last()
    if last_payroll:
        last_payroll_id = last_payroll.payroll_id
        payroll_number = int(last_payroll_id[7:]) + 1
        payroll_id = f'PAYROLL{str(payroll_number).zfill(3)}'
    else:
        payroll_id = 'PAYROLL001'
    

    if request.method == 'POST':
   
        emp_id = request.POST.get("emp_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        office_email = request.POST.get("office_email")
        first_name = request.POST.get("first_name")
        middle_name= request.POST.get("middle_name")
        last_name= request.POST.get("last_name")
        address= request.POST.get("address")
        state= request.POST.get("state")
        city= request.POST.get("city")
        country= request.POST.get("country")
        pin_code= request.POST.get("pin_code")
        c_address= request.POST.get("c_address")
        c_state= request.POST.get("c_state")
        c_city= request.POST.get("c_city")
        c_country= request.POST.get("c_country")
        c_pin_code= request.POST.get("c_pin_code")
        contact_no= request.POST.get("contact_no")
        other_contact_no= request.POST.get("other_contact_no")
        
        dob = request.POST.get("dob")
        doj = request.POST.get("doj")
        uanno= request.POST.get("uanno")

        pfno= request.POST.get("pfno")
        esicno= request.POST.get("esicno")
        pf_joining_date= request.POST.get("pf_joining_date")
       
        esic_joining_date= request.POST.get("pf_joining_date")
        try:
            

            dob_date = parse_date(dob)
            doj_date = parse_date(doj)
            pf_joining_date = parse_date(str(pf_joining_date))
            esic_joining_date = parse_date(str(esic_joining_date))
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        
        pancard_no= request.POST.get("pancard_no")
        aadhaarcard_no= request.POST.get("aadhaarcard_no")
        account_no= request.POST.get("account_no")
        bank_name= request.POST.get("bank_name")
        ifsc_code= request.POST.get("ifsc_code")
        branch= request.POST.get("branch")
        
        reporting_take = request.POST.get("reporting_take") == 'true'
       
        emergency_contactname = request.POST.get("emergency_contactname")
        emergency_contactnumber = request.POST.get("emergency_contactnumber")
        emergency_relationas = request.POST.get("emergency_relationas")

        
        department_id = request.POST.get("department")
        selectdepartment = Department.objects.get(pk=department_id)

        company_branch_id = request.POST.get("company_branch")
        company_branch = CompanyBranch.objects.get(pk=company_branch_id)

        designation_id = request.POST.get("designation")
        designation = Designation.objects.get(pk=designation_id)

        reporting_to_id = request.POST.get('reporting_to')
        if reporting_to_id:
            reporting_to = Employee.objects.get(pk=reporting_to_id)
        else:
            reporting_to = None


        position_id = request.POST.get("position")
        position = Position.objects.get(pk=position_id)

        gender_id = request.POST.get("gender")
        gender = Gender.objects.get(pk=gender_id)

        

        if candidate:
                employee_instance = Employee.objects.create(
                    candidate_id=candidate, 
                    emp_id=emp_id, 
                    name=name, 
                    first_name=first_name, 
                    middle_name=middle_name, 
                    last_name=last_name,
                    email=email,
                    office_email=office_email,
                    address=address, 
                    state=state, 
                    city=city, 
                    country=country, 
                    pin_code=pin_code,
                    c_address=c_address, 
                    c_state=c_state, 
                    c_city=c_city, 
                    c_country=c_country, 
                    c_pin_code=c_pin_code,
                    contact_no=contact_no, 
                    other_contact_no=other_contact_no,
                    dob=dob, 
                    doj=doj, 
                    pfno=pfno,
                    esicno=esicno,
                    pf_joining_date=pf_joining_date,
                    esic_joining_date=esic_joining_date,
                    uanno=uanno, 
                    pancard_no=pancard_no,
                    aadhaarcard_no=aadhaarcard_no, 
                    account_no=account_no, 
                    bank_name=bank_name, 
                    ifsc_code=ifsc_code, 
                    branch=branch,
                    reporting_take=reporting_take,
                    company_branch=company_branch,
                    department=selectdepartment,
                    designation=designation,
                    reporting_to=reporting_to,
                    position=position,
                    gender=gender,
                    emergency_contactname=emergency_contactname,
                    emergency_contactnumber=emergency_contactnumber,
                    emergency_relationas=emergency_relationas,
                )

                
                employee_instance.save()


        else:

            candidateresume_instance = candidateResume.objects.create(
            phone_number=contact_no,
            status="Shortlisted",
            interviewFeedback="IsEmployeeNow",
            interviewFeedback_date=datetime.now(),
            name=name,
            email=email,
            department=selectdepartment,
            designation=designation,
            resume="Not Required"
        )

            # Create a new Onboarding entry
            onboarding_instance = Onboarding.objects.create(
            candidate_id=candidateresume_instance,  # Make sure candidate is not None
            c_adhar="c_aadahar.jpg",
            c_pan="c_pan.jpg",
            c_bankDetails="c_bank.jpg",
            c_salarySlips="c_bank.jpg",
            c_expLetter="c_bank.jpg",
            c_previousJoiningLetter="c_ban.jpg",
            c_degree="c_bank.jpg",
            c_masters="c_bank.jpg",
            c_HSC="c_bank.jpg",
            c_SSC="c_bank.jpg",
            c_otherCertificate="c_bank.jpg"
        )


            # Increment doc_id by 1
            new_doc_id = onboarding_instance.doc_id + 1
            new_candidate_id = candidateresume_instance.candidate_id + 1
            # Create Employee instance and save doc_id
            employee_instance = Employee.objects.create(
                emp_id=emp_id, name=name, candidate_id=candidateresume_instance,
                first_name=first_name, middle_name=middle_name, last_name=last_name,email=email,office_email=office_email,
                address=address, state=state, city=city, country=country, pin_code=pin_code,
                c_address=c_address, c_state=c_state, c_city=c_city, c_country=c_country, c_pin_code=c_pin_code,
                contact_no=contact_no,other_contact_no=other_contact_no, dob=dob, doj=doj, pfno=pfno,esicno=esicno,pf_joining_date=pf_joining_date,esic_joining_date=esic_joining_date, uanno=uanno, pancard_no=pancard_no,
                aadhaarcard_no=aadhaarcard_no, account_no=account_no, bank_name=bank_name, ifsc_code=ifsc_code, branch=branch,reporting_take=reporting_take,company_branch=company_branch,department=selectdepartment,
                designation=designation,reporting_to=reporting_to,documents_id=onboarding_instance,position=position,gender=gender, emergency_contactname=emergency_contactname,
                emergency_contactnumber=emergency_contactnumber,emergency_relationas=emergency_relationas,
            )


            # Save the incremented doc_id in Employee model
            
            employee_instance.save()

        
        Payroll.objects.create(
            payroll_id=payroll_id,
            emp_id=employee_instance, 
           
    )
        messages.success(request, 'Employee Create successfully!')
        return redirect('hr:view_employee')
    context =   {
                    'emp_id': emp_id,
                    'emp':emp,
                    'candidate': candidate,
                    'department_all':department_all,
                    'candidate_c_psimg':candidate_c_psimg,
                    'documents':documents,
                    'company_branch':company_branch,
                    'position':position,
                    'gender':gender,
                }
    context.update(get_session(request))
    request.session.save()

    return render(request, 'hr/directemployee.html', context)



def add_department_details(request):
    if request.method == 'POST': 
        name = request.POST.get('name')

        try:
            # Check if department already exists
            existing_department = Department.objects.get(name=name)
            return JsonResponse({"error": "Department already exists"}, status=400)
        except ObjectDoesNotExist:
            # Department does not exist, create it
            try:
                Department.objects.create(name=name)
                return JsonResponse({'success': 'Department Add successfully!'})
            except Exception as e:
                return JsonResponse({'error': 'Interview round not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

           
def get_department_details(request, department_id):
    
    try:
        department_data = Department.objects.get(pk=department_id)
        data = {
            'id': department_data.id,
            'name': department_data.name,
        }

    
        

        return JsonResponse(data)
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


def update_department_details(request, department_id):
    if request.method == 'POST':
        try:
            department_data = Department.objects.get(pk=department_id)
            new_name = request.POST.get('name')

            # Check if the new name is the same as the existing name
            if new_name == department_data.name:
                return JsonResponse({'error': 'Department name remains unchanged'}, status=400)

            # Check if the new name already exists
            try:
                existing_department = Department.objects.get(name=new_name)
                return JsonResponse({'error': 'Department name already exists'}, status=400)
            except ObjectDoesNotExist:
                # If the new name doesn't exist, update the department
                department_data.name = new_name
                department_data.save()
                return JsonResponse({'success': 'Department updated successfully'})
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def delete_department(request, department_id):
    if request.method == 'POST':
        try:
            department = Department.objects.get(pk=department_id)
            department.delete()
            return JsonResponse({'success': 'Department deleted successfully'})
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
     

def add_designation_details(request):
    if request.method == 'POST': 
        department_name = request.POST.get('department')
        name = request.POST.get('name')

        try:
            # Get the department instance
            department_instance = Department.objects.get(name=department_name)
            # Check if designation already exists for the department
            if Designation.objects.filter(department=department_instance, name=name).exists():
                return JsonResponse({"error": "Designation already exists"}, status=400)
            else:
                # Create the designation
                Designation.objects.create(department=department_instance, name=name)
                return JsonResponse({"success": "Designation created successfully"})
        except Department.DoesNotExist:
            return JsonResponse({"error": "Department does not exist"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def get_designation_details(request, designation_id):
    try:
        designation = Designation.objects.get(pk=designation_id)
        data = {
            'id': designation.id,
            'department_id': designation.department_id,
            'name': designation.name,
        }
        return JsonResponse(data)
    except Designation.DoesNotExist:
        return JsonResponse({'error': 'Designation not found'}, status=404)

def update_designation_details(request, designation_id):
    if request.method == 'POST':
        try:
            designation = Designation.objects.get(pk=designation_id)
            department_id = request.POST.get('department')
            name = request.POST.get('name')

            # Check if a designation with the same department and name already exists
            if Designation.objects.exclude(pk=designation_id).filter(department_id=department_id, name=name).exists():
                return JsonResponse({'error': 'Designation already exists for the selected department'}, status=400)

            department = Department.objects.get(pk=department_id)
            designation.department = department
            designation.name = name
            designation.save()

            return JsonResponse({'success': 'Designation updated successfully'})
        except Designation.DoesNotExist:
            return JsonResponse({'error': 'Designation not found'}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def delete_designation(request, designation_id):
    if request.method == 'POST':
        try:
            designation = Designation.objects.get(pk=designation_id)
            designation.delete()
            return JsonResponse({'success': 'Designation deleted successfully'})
        except Designation.DoesNotExist:
            return JsonResponse({'error': 'Designation not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def add_position_details(request):
    if request.method == 'POST': 
        name = request.POST.get('name')
        remarks = request.POST.get('remarks')

        try:
            # Check if position already exists
            existing_position = Position.objects.get(name=name)
            return JsonResponse({"error": "Position already exists"}, status=400)
        except ObjectDoesNotExist:
            # Position does not exist, create it
            try:
                Position.objects.create(name=name,remarks=remarks)
                return redirect('hr:view_company')
            except Exception as e:
                return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def get_position_details(request, position_id):
    
    try:
        position_data = Position.objects.get(pk=position_id)
        data = {
            'id': position_data.id,
            'name': position_data.name,
            'remarks': position_data.remarks,
        }

       

        return JsonResponse(data)
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Position not found'}, status=404)


def update_position_details(request, position_id):
    if request.method == 'POST':
        try:
            position_data = Position.objects.get(pk=position_id)
            new_name = request.POST.get('name')
            new_remarks = request.POST.get('remarks')

            # Check if the new name already exists
            if Position.objects.filter(name=new_name).exclude(pk=position_id).exists():
                return JsonResponse({'error': 'Position name already exists'}, status=400)
            else:
                position_data.name = new_name
                position_data.remarks = new_remarks
                position_data.save()
                return JsonResponse({'success': 'Position updated successfully'})
        except Position.DoesNotExist:
            return JsonResponse({'error': 'Position not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def delete_position(request, position_id):
    if request.method == 'POST':
        try:
            position = Position.objects.get(pk=position_id)
            position.delete()
            return JsonResponse({'success': 'Position deleted successfully'})
        except Position.DoesNotExist:
            return JsonResponse({'error': 'Position not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def add_weekoff_details(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            remarks = request.POST.get('remarks')
            data = json.loads(request.POST.get('data'))

            existing_weekoff = WeekOff.objects.filter(name=name, remarks=remarks)
            if existing_weekoff.exists():
                return JsonResponse({"error": "Weekoff already exists"}, status=400)

            new_weekoff = WeekOff.objects.create(name=name, remarks=remarks)

            for week_data in data:
                week_no = week_data['week']
                days = week_data['days']
                week_no_instance = WeekOffNo.objects.create(weekoff=new_weekoff, week_no=week_no)
                for day_state in days:
                    WeekOffDay.objects.create(week_no=week_no_instance, week_day=day_state['day'], week_value=day_state['value'])

            return JsonResponse({"success": "Weekoff created successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def get_weekoff_details(request, weekoff_id):
    
    try:
        weekoff_data = WeekOff.objects.get(pk=weekoff_id)
        data = []
        for i in weekoff_data.weekoff_nos.all():
            week_data = WeekOffDay.objects.filter(week_no = i)
            week = {
                'week':i.week_no,
                'days':[]
            }
            for j in week_data:
                week['days'].append({'day':j.week_day, 'value':j.week_value})
            data.append(week)
        
        data = {
            'id': weekoff_data.id,
            'name': weekoff_data.name,
            'remarks':weekoff_data.remarks,
            'data' : data
            }

        return JsonResponse(data)
    except WeekOff.DoesNotExist:
        return JsonResponse({'error': 'Weekoff not found'}, status=404)
def update_weekoff_details(request, weekoff_id):
    if request.method == 'POST':
        try:
            weekoff_data = WeekOff.objects.get(pk=weekoff_id)
            name = request.POST.get('name')
            remarks = request.POST.get('remarks')
            data = json.loads(request.POST.get('data'))

            # Check if there's any other weekoff with the same name and remarks except the current one
            existing_weekoff = WeekOff.objects.exclude(pk=weekoff_id).filter(name=name, remarks=remarks)
            if existing_weekoff.exists():
                return JsonResponse({"error": "Weekoff already exists"}, status=400)

            # Update the existing weekoff details
            weekoff_data.name = name
            weekoff_data.remarks = remarks
            weekoff_data.save()

            # Clear existing weekoff details and add updated ones
            weekoff_data.weekoff_nos.all().delete()
            for week_data in data:
                week_no = week_data['week']
                days = week_data['days']
                week_no_instance = WeekOffNo.objects.create(weekoff=weekoff_data, week_no=week_no)
                for day_state in days:
                    WeekOffDay.objects.create(week_no=week_no_instance, week_day=day_state['day'], week_value=day_state['value'])

            return JsonResponse({"success": "Weekoff updated successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

def delete_weekoff(request, weekoff_id):
    if request.method == 'POST':
        try:
            weekoff = WeekOff.objects.get(pk=weekoff_id)
            # Delete related WeekOffDay instances
            WeekOffDay.objects.filter(week_no__weekoff=weekoff).delete()
            # Delete related WeekOffNo instances
            WeekOffNo.objects.filter(weekoff=weekoff).delete()
            # Delete the WeekOff instance
            weekoff.delete()
            return JsonResponse({'success': 'Weekoff deleted successfully'})
        except WeekOff.DoesNotExist:
            return JsonResponse({'error': 'Weekoff not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
      

def add_holidaymaster_details(request):
    if request.method == 'POST': 
        name = request.POST.get('name')  # Corrected to retrieve POST data
        year = request.POST.get('year') 
        remarks = request.POST.get('remarks') 
        try:
            # Check if department already exists
            existing_holidaymaster= HolidayMaster.objects.get(name=name,year=year)
            return JsonResponse({"error": "Department already exists"}, status=400)
        
        except ObjectDoesNotExist:
            
            try:

                HolidayMaster.objects.create(name=name,year=year,remarks=remarks)
                return JsonResponse({"success": "HolidayMaster created successfully"})
            except Exception as e:
                return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_holidaymaster_details(request, holidaymaster_id):
    
    try:
        holidaymaster_data = HolidayMaster.objects.get(pk=holidaymaster_id)
        data = {
            'id': holidaymaster_data.id,
            'name': holidaymaster_data.name,
            'year': holidaymaster_data.year,
            'remarks': holidaymaster_data.remarks,
        }

        
        

        return JsonResponse(data)
    except HolidayMaster.DoesNotExist:
        return JsonResponse({'error': 'HolidayMaster not found'}, status=404)



def update_holidaymaster_details(request, holidaymaster_id):
    if request.method == 'POST':
        try:
            holidaymaster_data = HolidayMaster.objects.get(pk=holidaymaster_id)
            new_name = request.POST.get('name')  # Assuming you're sending the updated name via POST request
            new_year = request.POST.get('year')
            new_remarks = request.POST.get('remarks')
            # Check if the new name is the same as the existing name
            if new_name == holidaymaster_data.name:
                return JsonResponse({'error': 'Holiday Master name remains unchanged'}, status=400)
            
            # Check if the new name already exists
            try:
                existing_holidaymaster = HolidayMaster.objects.get(name=new_name,year=new_year)
                return JsonResponse({'error': 'Holiday name year already exists'}, status=400)
            except ObjectDoesNotExist:

                holidaymaster_data.name = new_name
                holidaymaster_data.year = new_year
                holidaymaster_data.remarks = new_remarks
                holidaymaster_data.save()
                return JsonResponse({'success': 'HolidayMaster updated successfully'})
        except HolidayMaster.DoesNotExist:
            return JsonResponse({'error': 'HolidayMaster not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def delete_holidaymaster(request, holidaymaster_id):
    if request.method == 'POST':
        try:
            holidaymaster = HolidayMaster.objects.get(pk=holidaymaster_id)
            holidaymaster.delete()
            return JsonResponse({'success': 'Holiday master deleted successfully'})
        except HolidayMaster.DoesNotExist:
            return JsonResponse({'error': 'Holiday master not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
          

def  add_holiday_list_details(request):
    if request.method == 'POST': 
        

        holiday_master_id = request.POST.get('holiday_master')
        date = request.POST.get('date')
        festival_name = request.POST.get('festival_name')

        try:
            
            holiday_master_instance = HolidayMaster.objects.get(id=holiday_master_id)

            if HolidayList.objects.filter(holiday_master=holiday_master_instance, festival_name=festival_name,date=date).exists():
                return JsonResponse({'error': 'HolidayList already exists for the selected holidaymaster'}, status=400)
            else:
                HolidayList.objects.create(holiday_master=holiday_master_instance,festival_name=festival_name,date=date)
                return JsonResponse({"success": "HolidayList created successfully"})
        except HolidayMaster.DoesNotExist:
            return JsonResponse({"error": "HolidayMaster does not exist"}, status=400)
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def get_holiday_list_details(request, holiday_list_id):
    try:
        holiday_list = HolidayList.objects.get(pk=holiday_list_id)
        data = {
            'id': holiday_list.id,
            'holiday_master_id': holiday_list.holiday_master_id,
            'festival_name': holiday_list.festival_name,
            'date': holiday_list.date,
        }
        return JsonResponse(data)
    except HolidayList.DoesNotExist:
        return JsonResponse({'error': 'HolidayList not found'}, status=404)

def update_holiday_list_details(request, holiday_list_id):
    if request.method == 'POST':
        try:
            holiday_list = HolidayList.objects.get(pk=holiday_list_id)
            holiday_master_id = request.POST.get('holiday_master')
            festival_name = request.POST.get('festival_name')
            date = request.POST.get('date')
            
            # Check if a holiday_list with the same holiday_master and festival_name already exists
            if HolidayList.objects.exclude(pk=holiday_list_id).filter(holiday_master_id=holiday_master_id, festival_name=festival_name, date=date).exists():
                return JsonResponse({'error': 'HolidayList already exists for the selected holiday_master'}, status=400)
            
            holiday_master = HolidayMaster.objects.get(pk=holiday_master_id)
            holiday_list.holiday_master = holiday_master
            holiday_list.festival_name = festival_name
            holiday_list.date = date
            holiday_list.save()
            return JsonResponse({'success': 'HolidayList updated successfully'})
        except HolidayList.DoesNotExist:
            return JsonResponse({'error': 'HolidayList not found'}, status=404)
        except HolidayMaster.DoesNotExist:
            return JsonResponse({'error': 'HolidayMaster not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def delete_holiday_list(request, holiday_list_id):
    try:
        holiday_list = HolidayList.objects.get(pk=holiday_list_id)
        holiday_list.delete()
        return JsonResponse({'success': 'Holiday list deleted successfully'})
    except HolidayList.DoesNotExist:
        return JsonResponse({'error': 'Holiday list not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    



def add_payroll_details(request):
    if request.method == 'POST': 
        name = request.POST.get('name')

        try:
            # Check if payroll already exists
            existing_payroll = Payroll.objects.get(name=name)
            return JsonResponse({"error": "Payroll already exists"}, status=400)
        except ObjectDoesNotExist:
            # Payroll does not exist, create it
            try:
                Payroll.objects.create(name=name)
                return redirect('hr:view_company')
            except Exception as e:
                return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

           


def view_company(request):
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
    
    company_data = Company.objects.all()
    
    
        
    onboarding_exists = Onboarding.objects.all()
    
    
    if request.method == 'POST' and 'download_button' in request.POST:
        df = pd.DataFrame(list(company_data.values()))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="company_report.csv"'
        df.to_csv(response, index=False)
        return response
    else:
        context = {
            'company_data': company_data,
            'onboarding_exists':onboarding_exists,
            'daterange':daterange
            
            
        }

        context.update(get_session(request))  # Call get_session to retrieve the dictionary
        request.session.save()

    return render(request, 'Companylist.html', context)



#@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
@login_required(login_url=reverse_lazy('accounts:login'))
def company_profile(request, pk):
    company_data = Company.objects.get(pk=pk)
   
    
    company=Company.objects.all()
    
    department_all= Department.objects.all()
    designation_all= Designation.objects.all()
    position_all= Position.objects.all()
    holidaymaster_all= HolidayMaster.objects.all()
    holiday_list_all= HolidayList.objects.all()
    weekoff_all=WeekOff.objects.all()
    company_bank_all=CompanyBankDetails.objects.all()
    company_branch_all=CompanyBranch.objects.all()
    announcementmaster_all= Announcement.objects.all()
    policiesmaster_all= Policies.objects.all()
    company_payroll_all = CompanyPayrollDetails.objects.filter(company=company_data)


    context = {'company_data': company_data, 
               'company': company,
               'department_all':department_all,
               'designation_all':designation_all,
               'position_all':position_all,
               'holidaymaster_all':holidaymaster_all,
               'holiday_list_all':holiday_list_all,
               'weekoff_all':weekoff_all,
               'company_bank_all':company_bank_all,
               'company_branch_all':company_branch_all,
               'announcementmaster_all':announcementmaster_all,
               'policiesmaster_all':policiesmaster_all,
               'company_payroll_all':company_payroll_all
        }
    context.update(get_session(request))  # Call get_session to retrieve the dictionary
    request.session.save()
    return render(request, 'CompanyProfile.html', context)



from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def update_company_info(request, id):
    if request.method == 'POST':
        print((request.FILES))
        phone_no = Decimal(request.POST.get('phone_no'))
        website = request.POST.get('website')
        domain = request.POST.get('domain')
        email_id = request.POST.get('email_id')
        industries_type = request.POST.get('industries_type')
        
        gst_no = request.POST.get('gst_no')
        tin_no = request.POST.get('tin_no')
        cin_no = request.POST.get('cin_no')
        pancard_no = request.POST.get('pancard_no')
        aadhaarcard_no = request.POST.get('aadhaarcard_no')
        account_no = request.POST.get('account_no')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        branch = request.POST.get('branch')
        
        start_date = request.POST.get('start_date')

        
        status = request.POST.get('status')
        emp_id_series = request.POST.get('emp_id_series')
        reg_address = request.POST.get('reg_address')
        reg_city = request.POST.get('reg_city')
        reg_state = request.POST.get('reg_state')
        reg_country = request.POST.get('reg_country')
        reg_pin_code = request.POST.get('reg_pin_code')
        corp_address = request.POST.get('corp_address')
        corp_city = request.POST.get('corp_city')
        corp_state = request.POST.get('corp_state')
        corp_country = request.POST.get('corp_country')
        corp_pin_code = request.POST.get('corp_pin_code')
        
        company = Company.objects.get(id=id)
        
        company.phone_no = phone_no
        company.website = website
        company.domain = domain
        company.email_id = email_id
        company.industries_type = industries_type
        
        company.gst_no = gst_no
        company.tin_no = tin_no
        company.cin_no = cin_no
        company.pancard_no = pancard_no
        company.aadhaarcard_no = aadhaarcard_no
        company.account_no = account_no
        company.bank_name = bank_name
        company.ifsc_code = ifsc_code
        company.branch = branch
        company.start_date = start_date
        company.status = status
        company.emp_id_series = emp_id_series
        company.reg_address = reg_address
        company.reg_city = reg_city
        company.reg_state = reg_state
        company.reg_country = reg_country
        company.reg_pin_code = reg_pin_code
        company.corp_address = corp_address
        company.corp_city = corp_city
        company.corp_state = corp_state
        company.corp_country = corp_country
        company.corp_pin_code = corp_pin_code
        company.save()

        # Check if a new logo file is uploaded
        if 'logo' in request.FILES:
            # Delete the old logo file if it exists
            if company.logo and os.path.isfile(company.logo.path):
                try:
                    os.remove(company.logo.path)
                except FileNotFoundError:
                    print(f"File not found: {company.logo.path}")
            
            # Assign the new logo file
            company.logo = request.FILES['logo']
        else:
            return redirect('hr:company_profile', pk=id)
        company.save()

        messages.success(request, 'Company updated successfully.')
        return redirect('hr:company_profile', pk=id)
    else:
        return redirect('hr:company_profile', pk=id)

def add_payroll_list_details(request):
    if request.method == 'POST': 
        company_id = request.POST.get('company')
        basic = request.POST.get('basic')
        hra = request.POST.get('hra')
        ca = request.POST.get('ca')
        sa = request.POST.get('sa')
        pt = request.POST.get('pt')
        employer_pf = request.POST.get('employer_pf')
        employer_esic = request.POST.get('employer_esic')
        employee_pf = request.POST.get('employee_pf')
        employee_esic = request.POST.get('employee_esic')


        try:
            company_instance = Company.objects.get(id=company_id)  # Change here to get by ID

            if CompanyPayrollDetails.objects.filter(company=company_instance,basic=basic,hra=hra,ca=ca,sa=sa,pt=pt,employer_pf=employer_pf,employer_esic=employer_esic,employee_pf=employee_pf,employee_esic=employee_esic).exists():
                return JsonResponse({'error': 'Payroll already exists for the selected Company'}, status=400)
            
            CompanyPayrollDetails.objects.create(company=company_instance, basic=basic,hra=hra,ca=ca,sa=sa,pt=pt,employer_pf=employer_pf,employer_esic=employer_esic,employee_pf=employee_pf,employee_esic=employee_esic)
            return redirect('hr:view_company')
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_payroll_list_details(request, payroll_list_id):
    
    try:
        payroll_list = CompanyPayrollDetails.objects.get(pk=payroll_list_id)
        data = {
            'id': payroll_list.id,            
            'company_id' : payroll_list.company_id,
            'basic' : payroll_list.basic,
            'hra' : payroll_list.hra,
            'ca' : payroll_list.ca,
            'sa' : payroll_list.sa,
            'pt' : payroll_list.pt,
            'employer_pf' : payroll_list.employer_pf,
            'employer_esic' : payroll_list.employer_esic,
            'employee_pf' : payroll_list.employee_pf,
            'employee_esic' : payroll_list.employee_esic,
        }
        return JsonResponse(data)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Payroll not found'}, status=404)

def update_payroll_list_details(request, payroll_list_id):
    if request.method == 'POST':
        try:
            payroll_list = CompanyPayrollDetails.objects.get(pk=payroll_list_id)
            company_id = request.POST.get('company')
            basic = request.POST.get('basic')
            hra = request.POST.get('hra')
            ca = request.POST.get('ca')
            sa = request.POST.get('sa')
            pt = request.POST.get('pt')
            employer_pf = request.POST.get('employer_pf')
            employer_esic = request.POST.get('employer_esic')
            employee_pf = request.POST.get('employee_pf')
            employee_esic = request.POST.get('employee_esic')

            # Try to get the company object based on the provided company ID
            company = get_object_or_404(Company, pk=company_id)

            # Update the payroll list details
            payroll_list.company = company
            payroll_list.basic = basic
            payroll_list.hra = hra
            payroll_list.ca = ca
            payroll_list.sa = sa
            payroll_list.pt = pt
            payroll_list.employer_pf = employer_pf
            payroll_list.employer_esic = employer_esic
            payroll_list.employee_pf = employee_pf
            payroll_list.employee_esic = employee_esic
            
            payroll_list.save()

            return JsonResponse({'success': 'Payroll list updated successfully!'})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except CompanyPayrollDetails.DoesNotExist:
            return JsonResponse({'error': 'Payroll details not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def delete_payroll_list(request, payroll_list_id):
    if request.method == 'POST':
        try:
            payroll_list = CompanyPayrollDetails.objects.get(pk=payroll_list_id)
            payroll_list.delete()
            return JsonResponse({'success': 'Payroll list deleted successfully'})
        except CompanyPayrollDetails.DoesNotExist:
            return JsonResponse({'error': 'Payroll list not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def add_bank_list_details(request):
    if request.method == 'POST': 
        company_id = request.POST.get('company')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        branch = request.POST.get('branch')
        account_no = request.POST.get('account_no')
        remarks = request.POST.get('remarks')
        status = request.POST.get('status')
        try:
            company_instance = Company.objects.get(id=company_id)  # Change here to get by ID

            if CompanyBankDetails.objects.filter(company=company_instance, bank_name=bank_name,ifsc_code=ifsc_code,branch=branch,account_no=account_no,remarks=remarks,status=status).exists():
                return JsonResponse({'error': 'Bank already exists for the selected Bank'}, status=400)
            
            CompanyBankDetails.objects.create(company=company_instance, bank_name=bank_name,ifsc_code=ifsc_code,branch=branch,account_no=account_no,remarks=remarks,status=status)
            return redirect('hr:view_company')
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_bank_list_details(request, bank_list_id):
    
    try:
        bank_list = CompanyBankDetails.objects.get(pk=bank_list_id)
        data = {
            'id': bank_list.id,
            'company_id': bank_list.company_id,
            'bank_name': bank_list.bank_name,
            'ifsc_code': bank_list.ifsc_code,
            'branch': bank_list.branch,
            'account_no': bank_list.account_no,
            'remarks': bank_list.remarks,
            'status':bank_list.status,
        }
        return JsonResponse(data)
    except HolidayList.DoesNotExist:
        return JsonResponse({'error': 'Bank not found'}, status=404)

def update_bank_list_details(request, bank_list_id):
    if request.method == 'POST':
        try:
            bank_list = CompanyBankDetails.objects.get(pk=bank_list_id)
            company_id = request.POST.get('company')
            bank_name = request.POST.get('bank_name')
            ifsc_code = request.POST.get('ifsc_code')
            branch = request.POST.get('branch')
            account_no = request.POST.get('account_no')
            remarks = request.POST.get('remarks')
            status = request.POST.get('status')

            # Try to get the company object based on the provided company ID
            company = get_object_or_404(Company, pk=company_id)

            # Update the bank list details
            bank_list.company = company
            bank_list.bank_name = bank_name
            bank_list.ifsc_code = ifsc_code
            bank_list.branch = branch
            bank_list.account_no = account_no
            bank_list.remarks = remarks
            bank_list.status=status
            bank_list.save()

            return JsonResponse({'success': 'Bank list updated successfully!'})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except CompanyBankDetails.DoesNotExist:
            return JsonResponse({'error': 'Bank details not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def delete_bank_list(request, bank_list_id):
    if request.method == 'POST':
        try:
            bank_list = CompanyBankDetails.objects.get(pk=bank_list_id)
            bank_list.delete()
            return JsonResponse({'success': 'Bank list deleted successfully'})
        except CompanyBankDetails.DoesNotExist:
            return JsonResponse({'error': 'Bank list not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
     

def add_branch_list_details(request):
    if request.method == 'POST': 
        company_id = request.POST.get('company')
        name = request.POST.get('name')
        address = request.POST.get('address')
        state = request.POST.get('state')
        city = request.POST.get('city')
        country = request.POST.get('country')
        pin_code = request.POST.get('pin_code')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')
        start_date = request.POST.get('start_date')
        status = request.POST.get('status')

        try:
            company_instance = Company.objects.get(id=company_id)  # Change here to get by ID

            if CompanyBranch.objects.filter(company=company_instance, name=name,address=address,state=state,city=city,country=country,pin_code=pin_code,email=email,contact_no=contact_no,start_date=start_date,status=status).exists():
                return JsonResponse({'error': 'Bank already exists for the selected Bank'}, status=400)
            
            CompanyBranch.objects.create(company=company_instance, name=name,address=address,state=state,city=city,country=country,pin_code=pin_code,email=email,contact_no=contact_no,start_date=start_date,status=status)
            return redirect('hr:view_company')
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_branch_list_details(request, branch_list_id):
    
    try:
        branch_list = CompanyBranch.objects.get(pk=branch_list_id)
        data = {
            'id': branch_list.id,            
            'company_id' : branch_list.company_id,
            'name' : branch_list.name,
            'address' : branch_list.address,
            'state' : branch_list.state,
            'city' : branch_list.city,
            'country' : branch_list.country,
            'pin_code' : branch_list.pin_code,
            'email' : branch_list.email,
            'contact_no' : branch_list.contact_no,
            'start_date' : branch_list.start_date,
            'end_date' : branch_list.end_date,
            'status' : branch_list.status,
        }
        return JsonResponse(data)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Branch not found'}, status=404)

def update_branch_list_details(request, branch_list_id):
    if request.method == 'POST':
        try:
            branch_list = CompanyBranch.objects.get(pk=branch_list_id)
            company_id = request.POST.get('company')
            name = request.POST.get('name')
            address = request.POST.get('address')
            state = request.POST.get('state')
            city = request.POST.get('city')
            country = request.POST.get('country')
            pin_code = request.POST.get('pin_code')
            email = request.POST.get('email')
            contact_no = request.POST.get('contact_no')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            status = request.POST.get('status')

            # Try to get the company object based on the provided company ID
            company = get_object_or_404(Company, pk=company_id)

            # Parse and validate start date
            start_date = parse_date(start_date_str)
            if not start_date:
                raise ValidationError('Invalid start date format. Must be in YYYY-MM-DD format.')

            # Parse and validate end date (if provided)
            if end_date_str:
                end_date = parse_date(end_date_str)
                if not end_date:
                    raise ValidationError('Invalid end date format. Must be in YYYY-MM-DD format.')

            # Update the branch list details
            branch_list.company = company
            branch_list.name = name
            branch_list.address = address
            branch_list.state = state
            branch_list.city = city
            branch_list.country = country
            branch_list.pin_code = pin_code
            branch_list.email = email
            branch_list.contact_no = contact_no
            branch_list.start_date = start_date
            branch_list.end_date = end_date if end_date_str else None
            branch_list.status = status
            branch_list.save()

            return JsonResponse({'success': 'Branch list updated successfully!'})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except CompanyBranch.DoesNotExist:
            return JsonResponse({'error': 'Branch details not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def delete_branch_list(request, branch_list_id):
    if request.method == 'POST':
        try:
            branch_list = CompanyBranch.objects.get(pk=branch_list_id)
            branch_list.delete()
            return JsonResponse({'success': 'Branch list deleted successfully'})
        except CompanyBranch.DoesNotExist:
            return JsonResponse({'error': 'Branch list not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
     




def add_policy_list_details(request):
    if request.method == 'POST': 
        company_id = request.POST.get('company')
        name = request.POST.get('name')
        created_on = request.POST.get('created_on')
        remarks = request.POST.get('remarks')
        file = request.POST.get('file')
        status = request.POST.get('status')
        

        try:
            company_instance = Company.objects.get(id=company_id)  # Change here to get by ID

            if Policies.objects.filter(company=company_instance, name=name,created_on=created_on,remarks=remarks,file=file,status=status).exists():
                return JsonResponse({'error': 'Bank already exists for the selected Bank'}, status=400)
            
            Policies.objects.create(company=company_instance, name=name,created_on=created_on,remarks=remarks,file=file,status=status)
            return redirect('hr:view_company')
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_policy_list_details(request, policy_list_id):
    
    try:
        policy_list = Policies.objects.get(pk=policy_list_id)
        data = {
            'id': policy_list.id,            
            'company_id' : policy_list.company_id,
            'name' : policy_list.name,
            'created_on' : policy_list.created_on,
            'remarks' : policy_list.remarks,
            'file_url': policy_list.file.url if policy_list.file else None,  # Get file URL
            
            'status' : policy_list.status,
          
        }
        return JsonResponse(data)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Policy not found'}, status=404)

def update_policy_list_details(request, policy_list_id):
    if request.method == 'POST':
        try:
            policy_list = Policies.objects.get(pk=policy_list_id)
            company_id = request.POST.get('company')
            name = request.POST.get('name')
            created_on = request.POST.get('created_on')
            remarks = request.POST.get('remarks')
            file = request.POST.get('file')
            status = request.POST.get('status')
           

            # Try to get the company object based on the provided company ID
            company = get_object_or_404(Company, pk=company_id)

            # Update the policy list details
      
            policy_list.company = company
            policy_list.name = name
            policy_list.created_on = created_on
            policy_list.remarks = remarks
            policy_list.file = file
            policy_list.status = status

            # Check if a new  file is uploaded
            if 'file' in request.FILES:
                # Delete the old logo file if it exists
                if policy_list.file:
                    os.remove(policy_list.file.path)
                # Assign the new logo file
                policy_list.file = request.FILES['file']
            
            else:
                pass
           
            policy_list.save()

            return JsonResponse({'success': 'Policy list updated successfully!'})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Policies.DoesNotExist:
            return JsonResponse({'error': 'Policy details not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def delete_policy_list(request, policy_list_id):
    if request.method == 'POST':
        try:
            policy_list = Policies.objects.get(pk=policy_list_id)
            policy_list.delete()
            return JsonResponse({'success': 'Policy deleted successfully'})
        except Policies.DoesNotExist:
            return JsonResponse({'error': 'Policy not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
          

def announcement_list(request):
    context = get_session(request)
    emp_data = Employee.objects.all()
    company=Company.objects.all()
    announcementmaster_all= Announcement.objects.all()
 
    context.update({
        'emp_data': emp_data,
        'company':company,
        'announcementmaster_all':announcementmaster_all,
       
    })
    
    request.session.save()
    return render(request, 'hr/announcement.html', context)



def add_announcement_list_details(request):
    if request.method == 'POST': 
        company_id = request.POST.get('company')
        name = request.POST.get('name')
        created_on = request.POST.get('created_on')
        message = request.POST.get('message')
        file = request.POST.get('file')
        status = request.POST.get('status')

        try:
            company_instance = Company.objects.get(id=company_id)  # Change here to get by ID

            if Announcement.objects.filter(company=company_instance, name=name,created_on=created_on,message=message,file=file,status=status).exists():
                return JsonResponse({'error': 'Announcement already exists for the selected company'}, status=400)
            
            Announcement.objects.create(company=company_instance, name=name,created_on=created_on,message=message,file=file,status=status)
            return redirect('hr:announcement_list')
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_announcement_list_details(request, announcement_list_id):
    try:
        announcement_list = Announcement.objects.get(pk=announcement_list_id)
        data = {
            'id': announcement_list.id,            
            'company_id' : announcement_list.company_id,
            'name' : announcement_list.name,
            'created_on' : announcement_list.created_on,
            'message' : announcement_list.message,
            'file_url': announcement_list.file.url if announcement_list.file else None,  # Get file URL
            'status' : announcement_list.status,
        }
        return JsonResponse(data)
    except Announcement.DoesNotExist:
        return JsonResponse({'error': 'Announcement not found'}, status=404)
def update_announcement_list_details(request, announcement_list_id):
    if request.method == 'POST':
        try:
            announcement_list = Announcement.objects.get(pk=announcement_list_id)
            company_id = request.POST.get('company')
            name = request.POST.get('name')
            created_on = request.POST.get('created_on')
            message = request.POST.get('message')
            file = request.POST.get('file')
            status = request.POST.get('status')
           

            # Try to get the company object based on the provided company ID
            company = get_object_or_404(Company, pk=company_id)

            # Update the announcement list details
      
            announcement_list.company = company
            announcement_list.name = name
            announcement_list.created_on = created_on
            announcement_list.message = message
       
            announcement_list.status = status

            # Check if a new  file is uploaded
            if 'file' in request.FILES:
                # Delete the old logo file if it exists
                if announcement_list.file:
                    os.remove(announcement_list.file.path)
                # Assign the new logo file
                announcement_list.file = request.FILES['file']
            
            else:
                pass

            announcement_list.save()

            return JsonResponse({'success': 'Announcement list updated successfully!'})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Announcement.DoesNotExist:
            return JsonResponse({'error': 'Announcement details not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def delete_announcement_list(request, announcement_list_id):
    if request.method == 'POST':
        try:
            announcement_list = Announcement.objects.get(pk=announcement_list_id)
            announcement_list.delete()
            return JsonResponse({'success': 'Announcement list deleted successfully'})
        except Announcement.DoesNotExist:
            return JsonResponse({'error': 'Announcement list not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
          