from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from . import views

app_name = 'hr'

urlpatterns = [
    
    path('admin_dashboard',views.admin_dashboard,name="admin_dashboard"),
    path('hr_dashboard',views.hr_dashboard,name="hr_dashboard"),
 

    #<----------------- Resumes Datatable ------------------------------------------------------------->

    path('resumes/', views.resume_list, name='resume_list'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('resumes/preview/<int:resume_id>/', views.preview_resume, name='preview_resume'),
    path('resumes/edit/<int:resume_id>/', views.edit_resume, name='edit_resume'),
    path('hr/update_interview_remarks/', views.update_interview_remarks_view, name='update_interview_remarks'),
    path('upload-new-resume/<int:candidate_id>/', views.upload_new_resume, name='uploadNewResume'),
    path('create-interview/', views.create_interview, name='createInterview'),
    path('save-interview-feedback/<int:candidate_id>/', views.save_interview_feedback, name='saveInterviewFeedback'),

    #<----------------- Interviews Datatable ---------------------------------------------------------->
    path('get_interviewround_list_id_details/<int:id>/', views.get_interviewround_list_id_details, name='get_interviewround_list_id_details'),

    path('update_interviewround/', views.update_interviewround, name='update_interviewround'),

    path('schedule-interview/<int:candidate_id>/', views.schedule_interview, name='scheduleInterview'),

    #<----------------- Onboarding Datatable ---------------------------------------------------------->
    path('onboardings/', views.onboarding_list, name='onboarding_list'),
    path('onboarding-process/<int:onboarding_id>/', views.onboarding_process, name='onboardingProcess'),
    path('view_documents/<int:candidate_id>/', views.view_documents, name='view_documents'),
    path('updateimg<int:pk>',views.updateimg,name="updateimg"),

    path('updateaadhar<int:pk>/', views.updateaadhar, name="updateaadhar"),
    path('updatepan<int:pk>/', views.updatepan, name="updatepan"),
    path('updatebankdetails<int:pk>/', views.updatebankdetails, name="updatebankdetails"),
    path('updatebankstatement<int:pk>/', views.updatebankstatement, name="updatebankstatement"),
    path('updatesalaryslips<int:pk>/', views.updatesalaryslips, name="updatesalaryslips"),
    path('skipsalaryslips<int:pk>/', views.skipsalaryslips, name="skipsalaryslips"),
    path('updateexpletter<int:pk>/', views.updateexpletter, name="updateexpletter"),
    path('updatepreviousjoiningletter<int:pk>/', views.updatepreviousjoiningletter, name="updatepreviousjoiningletter"),
    path('updatec_degree<int:pk>/', views.updatec_degree, name="updatec_degree"),
    path('updatemasters<int:pk>/', views.updatemasters, name="updatemasters"),
    path('updatehsc<int:pk>/', views.updatehsc, name="updatehsc"),
    path('updatessc<int:pk>/', views.updatessc, name="updatessc"),
    path('updateothercertificate<int:pk>/', views.updateothercertificate, name="updateothercertificate"),
    path('updateresume<int:pk>/', views.updateresume, name="updateresume"),
   
    #<----------------- Employees ---------------------------------------->
    path('view_employee/', views.view_employee, name='view_employee'),
    path('add_employee/<int:pk>/', views.add_employee, name='add_employee'),
    path('check_email_exists/', views.check_email_exists, name='check_email_exists'),
    path('check_contact_no_exists/', views.check_contact_no_exists, name='check_contact_no_exists'),
    #<-----------------Direct Employees ---------------------------------------->
    path('direct_employee/', views.direct_employee, name='direct_employee'),
    
    #<----------------- Employee Profile Tabs URL --------------------------------------------------------------------->

    path('employee_profile/<str:id>/', views.employee_profile, name='employee_profile'),
    path('update_personal_info/<str:id>/', views.update_personal_info, name='update_personal_info'),
    path('update_work_info/<str:id>/', views.update_work_info, name='update_work_info'),
    path('update_team_info/<str:id>/', views.update_team_info, name='update_team_info'),
    path('update_payroll_info/<str:id>/', views.update_payroll_info, name='update_payroll_info'),
    path('update_bank_info/<str:id>/', views.update_bank_info, name='update_bank_info'),
    path('update_permission_info/<str:id>/', views.update_permission_info, name='update_permission_info'),

    
    #<----------------- Employees Ajax----------------------------------->
    path('ajax/ajax_newdepartment/', views.ajax_newdepartment, name='ajax_newdepartment'),
    path('ajax/ajax_adddesignation/', views.ajax_adddesignation, name='ajax_adddesignation'),
    path('ajax/load_designation/', views.load_designation, name='ajax_load_designation'),
    path('ajax_load_reporting_managers/', views.ajax_load_reporting_managers, name='ajax_load_reporting_managers'),
    path('ajax/load_interviewer/', views.ajax_load_interviewer, name='ajax_load_interviewer'),
    
    
    #<----------------- Attendance --------------------------------------------------------------------->
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    re_path(r'^attendance-report/(?P<emp_id>[A-Z]{5}\d{3})/$', views.attendance_report, name='attendance_report'),
    re_path(r'^ajax_load_PunchIn_PunchOut/(?P<emp_id>[A-Z]{5}\d{3})/(?P<selectedDate>\d{1,2}-\d{1,2}-\d{4})/$', views.ajax_load_PunchIn_PunchOut, name='ajax_load_PunchIn_PunchOut'),
    re_path(r'^ajax_save_attendance/(?P<emp_id>[A-Z]{5}\d{3})/(?P<selectedDate>\d{4}-\d{1,2}-\d{1,2})/$', views.ajax_save_attendance, name='ajax_save_attendance'),

    #<----------------- Company Profile Tabs URL --------------------------------------------------------------------->
    
    #<----------------- Company Profile Tabs URL ----------------->
    path('view_company/', views.view_company, name='view_company'),
    path('company_profile/<int:pk>/', views.company_profile, name='company_profile'),
    path('update_company_info/<str:id>/', views.update_company_info, name='update_company_info'),
    
    #<----------------- Company Payroll Tabs URL ----------------->
    path('add_payroll_list_details/', views.add_payroll_list_details, name='add_payroll_list_details'),
    path('get_payroll_list_details/<int:payroll_list_id>/', views.get_payroll_list_details, name='get_payroll_list_details'),
    path('update_payroll_list_details/<int:payroll_list_id>/', views.update_payroll_list_details, name='update_payroll_list_details'),
    path('delete_payroll_list/<int:payroll_list_id>/', views.delete_payroll_list, name='delete_payroll_list'),


    #<----------------- Company Bank Tabs URL ----------------->
    path('add_bank_list_details/', views.add_bank_list_details, name='add_bank_list_details'),
    path('get_bank_list_details/<int:bank_list_id>/', views.get_bank_list_details, name='get_bank_list_details'),
    path('update_bank_list_details/<int:bank_list_id>/', views.update_bank_list_details, name='update_bank_list_details'),
    path('delete_bank_list/<int:bank_list_id>/', views.delete_bank_list, name='delete_bank_list'),

    #<----------------- Company Branch Tabs URL ----------------->
    path('add_branch_list_details/', views.add_branch_list_details, name='add_branch_list_details'),
    path('get_branch_list_details/<int:branch_list_id>/', views.get_branch_list_details, name='get_branch_list_details'),
    path('update_branch_list_details/<int:branch_list_id>/', views.update_branch_list_details, name='update_branch_list_details'),
    path('delete_branch_list/<int:branch_list_id>/', views.delete_branch_list, name='delete_branch_list'),

    #<----------------- Company Department Tabs URL ----------------->
    path('get_department_details/<int:department_id>/', views.get_department_details, name='get_department_details'),
    path('update_department_details/<int:department_id>/', views.update_department_details, name='update_department_details'),
    path('add_department_details/', views.add_department_details, name='add_department_details'),
    path('delete_department/<int:department_id>/', views.delete_department, name='delete_department'),


    #<----------------- Company Designation Tabs URL ----------------->
    path('add_designation_details/', views.add_designation_details, name='add_designation_details'),
    path('get_designation_details/<int:designation_id>/', views.get_designation_details, name='get_designation_details'),
    path('update_designation_details/<int:designation_id>/', views.update_designation_details, name='update_designation_details'),
    path('delete_designation/<int:designation_id>/', views.delete_designation, name='delete_designation'),


    #<----------------- Company Position Tabs URL ----------------->
    path('get_position_details/<int:position_id>/', views.get_position_details, name='get_position_details'),
    path('update_position_details/<int:position_id>/', views.update_position_details, name='update_position_details'),
    path('add_position_details/', views.add_position_details, name='add_position_details'),
    path('delete_position/<int:position_id>/', views.delete_position, name='delete_position'),


    #<----------------- Company Week Off Tabs URL ----------------->
    path('add_weekoff_details/', views.add_weekoff_details, name='add_weekoff_details'),
    path('get_weekoff_details/<int:weekoff_id>/', views.get_weekoff_details, name='get_weekoff_details'),
    path('update_weekoff_details/<int:weekoff_id>/', views.update_weekoff_details, name='update_weekoff_details'),
    path('delete_weekoff/<int:weekoff_id>/', views.delete_weekoff, name='delete_weekoff'),

    #<----------------- Company Holiday Master Tabs URL ----------------->
    path('add_holidaymaster_details/', views.add_holidaymaster_details, name='add_holidaymaster_details'),
    path('get_holidaymaster_details/<int:holidaymaster_id>/', views.get_holidaymaster_details, name='get_holidaymaster_details'),
    path('update_holidaymaster_details/<int:holidaymaster_id>/', views.update_holidaymaster_details, name='update_holidaymaster_details'),
    path('delete_holidaymaster/<int:holidaymaster_id>/', views.delete_holidaymaster, name='delete_holidaymaster'),

    #<----------------- Company Holiday Festival List Tabs URL ----------------->
    path('add_holiday_list_details/', views.add_holiday_list_details, name='add_holiday_list_details'),
    path('get_holiday_list_details/<int:holiday_list_id>/', views.get_holiday_list_details, name='get_holiday_list_details'),
    path('update_holiday_list_details/<int:holiday_list_id>/', views.update_holiday_list_details, name='update_holiday_list_details'),
    path('delete_holiday_list/<int:holiday_list_id>/', views.delete_holiday_list, name='delete_holiday_list'),



   

    #<----------------- Company Policy Tabs URL ----------------->
    path('add_policy_list_details/', views.add_policy_list_details, name='add_policy_list_details'),
    path('get_policy_list_details/<int:policy_list_id>/', views.get_policy_list_details, name='get_policy_list_details'),
    path('update_policy_list_details/<int:policy_list_id>/', views.update_policy_list_details, name='update_policy_list_details'),
    path('delete_policy_list/<int:policy_list_id>/', views.delete_policy_list, name='delete_policy_list'),
    
    #<----------------- Company Announcement URL ----------------->
    path('announcement_list/', views.announcement_list, name='announcement_list'),
    path('add_announcement_list_details/', views.add_announcement_list_details, name='add_announcement_list_details'),
    path('get_announcement_list_details/<int:announcement_list_id>/', views.get_announcement_list_details, name='get_announcement_list_details'),
    path('update_announcement_list_details/<int:announcement_list_id>/', views.update_announcement_list_details, name='update_announcement_list_details'),
    path('delete_announcement_list/<int:announcement_list_id>/', views.delete_announcement_list, name='delete_announcement_list'),
    
    
]   