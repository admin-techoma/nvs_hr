from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'report'

urlpatterns = [

    

    path('employee_report/', views.employee_report, name='employee_report'),
    path('employeedata',views.employeedata,name='employeedata'),


    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('attendancedata',views.attendancedata,name='attendancedata'),

    path('leave_report/', views.leave_report, name='leave_report'),
    path('leavedata',views.leavedata,name='leavedata'),


    path('view_payrollreport/', views.view_payrollreport, name='view_payrollreport'),
    path('payrollreportdata/', views.payrollreportdata, name='payrollreportdata'),


    path('salary_report/', views.salary_report, name='salary_report'),
    path('salarydata',views.salarydata,name='salarydata'),

    path('resign_report/', views.resign_report, name='resign_report'),
    path('resigndata',views.resigndata,name='resigndata'),

    path('document_report/', views.document_report, name='document_report'),
    path('documentdata',views.documentdata,name='documentdata'),
    path('download_documents/', views.download_documents, name='download_documents'),

    path('interviews_report/', views.interviews_report, name='interviews_report'),
    path('interviewsdata',views.interviewsdata,name='interviewsdata'),

    path('track-interviewsreport/', views.track_interviewsreport, name='track_interviewsreport'),
    path('track_interviewsdatareport',views.track_interviewsdatareport,name='track_interviewsdatareport'),
    
  
    path('onboarding_report/', views.onboarding_report, name='onboarding_report'),
    path('onboardingdata_report',views.onboardingdata_report,name='onboardingdata_report'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
