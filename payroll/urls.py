from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
app_name = 'payroll'
urlpatterns = [
    #<----------------- Payroll------------------------------------------>
    path('add_payroll/<str:pk>/',views.add_payroll,name='add_payroll'),
    #<----------------- Employees Monthly Salary-------------------------------------------->
    path('month_salary/', views.month_salary, name='month_salary'),
    path('generate_salary/', views.generate_salary, name='generate_salary'),
    path('view_beforegenerate_salary/<str:pk>/', views.view_beforegenerate_salary, name='view_beforegenerate_salary'),
    path('edit_beforegenerate_salary/<str:pk>/', views.edit_beforegenerate_salary, name='edit_beforegenerate_salary'),
    # path('month_salarylist/', views.month_salarylist, name='month_salarylist'),
    path('create_salary/<str:pk>/', views.create_salary, name='create_salary'),
    path('month_salaryslip/<str:pk>/', views.month_salaryslip, name='month_salaryslip'),
    path('convert_html_to_pdf/<int:pk>/', views.download_salary_pdf, name='download_salary_pdf'),
    path('mail_salaryslip_pdf/<int:pk>/', views.mail_salaryslip_pdf, name='mail_salaryslip_pdf'),
    path('view_generatesalary/', views.view_generatesalary, name='view_generatesalary'),
    path('view_salary/<int:pk>/', views.view_salary, name='view_salary'),
    path('edit_salary/<str:id>/', views.edit_salary, name='edit_salary'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)