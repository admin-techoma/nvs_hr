from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from employee import views

app_name = 'employee'

urlpatterns = [
    
    #<----------------- Employees Dashboard--------------------------------------------------->
    path('dash',views.dash,name="dash"),

    #<----------------- Reporting Manager Dashboard--------------------------------------------------->
    path('rmdash',views.rmdash,name="rmdash"),

    #<----------------- Employees Clock In  URL--------------------------------------------------->
    re_path(r'^mark-clockIn/(?P<emp_id>[A-Z]{5}\d{3})/$', views.mark_clockIn, name='mark_clockIn'),
    re_path(r'^mark-clockOut/(?P<emp_id>[A-Z]{5}\d{3})/$', views.mark_clockOut, name='mark_clockOut'),


    #<----------------- Employees Profile URL--------------------------------------------------->

    path('view_profile/', views.view_profile, name='view_profile'),

    #<----------------- Employees Profile Password Change on Header option--------------------------------------------------->
    path('password_change/<str:emp_id>/', views.password_change, name='password_change'),

    #<----------------- Employees Attendance URL-------------------------------------------->
    path('attendance/', views.attendance, name='attendance'),
    path('employee_attendance/<str:employee_id>/', views.employee_attendance, name='employee_attendance'),
    path('employee_leave_data/<str:employee_id>/', views.employee_leave_data, name='employee_leave_data'),
    path('regularization_request/', views.request_regularization, name='regularization_request'),
   path('regularization_approve/<str:id>/', views.approve_regularization, name='approve_regularization'),
    
    #<----------------- Employees Leave URL-------------------------------------------->
    path('leaves_lists/', views.leaves_lists, name='leaves_lists'),
    re_path(r'^apply_leave/(?P<emp_id>[A-Z]{5}\d{3})/$', views.apply_leave, name='apply_leave'),
    path('update_leave_status/', views.update_leave_status, name='update_leave_status'),
    path('delete_leave/<str:leaveID>/', views.delete_leave, name='delete_leave'),

    #<----------USe for Employees Attendance Calender Card and View Before Generate Salary Page----------------------------------------------------->
    path('employee_monthly_data/<str:employee_id>/<int:year>/<int:month>/', views.employee_monthly_data, name='employee_monthly_data'),

    #<----------------- Employees Resign URL----------------------------------------------------->
    path('resign_lists/', views.resign_lists, name='resign_lists'),
    path('apply_resign/<str:employee_id>/', views.apply_resign, name='apply_resign'),
    path('update_resign_status/', views.update_resign_status, name='update_resign_status'),
    path('delete_resign_list/<int:resign_list_id>/', views.delete_resign_list, name='delete_resign_list'),

    #<----------------- Employees Payroll URL----------------------------------------------------->
    path('view_payroll/', views.view_payroll, name='view_payroll'),
    path('employee/download_pdf/<int:salary_id>/', views.download_pdf, name='download_pdf'),
   
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
