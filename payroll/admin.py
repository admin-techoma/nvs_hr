from django.contrib import admin

from payroll.models import Payroll,Monthly_salary

# Register your models here.
admin.site.register(Payroll)
admin.site.register(Monthly_salary)
# admin.site.register(Month_salary)