from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from payroll.models import Payroll, Monthly_salary

# Resource classes for import/export
class PayrollResource(resources.ModelResource):
    class Meta:
        model = Payroll
        import_id_fields = ['payroll_id']
@admin.register(Payroll)
class PayrollAdmin(ImportExportModelAdmin):
    resource_class = PayrollResource
    list_display = ['payroll_id', 'emp_id', 'ctc', 'basic', 'hra', 'ca', 'sa', 'employee_pf', 
                    'employer_pf', 'employee_esic', 'employer_esic', 'pt', 'gmc', 'tds', 
                    'vpf', 'gross_salary', 'total_deduction', 'net_salary', 'gratuity', 
                    'otherone', 'monthly_ctc', 'payment_cycle', 'applicable_from', 
                    'remarks', 'status', 'paymentmode', 'yearlyctc']

class MonthlySalaryResource(resources.ModelResource):
    class Meta:
        model = Monthly_salary

@admin.register(Monthly_salary)
class MonthlySalaryAdmin(ImportExportModelAdmin):
    resource_class = MonthlySalaryResource
    list_display = ['payroll_id', 'emp_id', 'month', 'year', 'salary_createdon', 
                    'payment_status', 'remarks', 'name', 'email', 'fixed_ctc', 
                    'fixed_basic', 'fixed_hra', 'fixed_ca', 'fixed_sa', 
                    'fixed_employeepf', 'fixed_employerpf', 'fixed_employeeesic', 
                    'fixed_employeresic', 'fixed_gross_salary', 'fixed_newctc', 
                    'fixed_professionalTax', 'fixed_total_deducation', 'fixed_netpay', 
                    'monthly_ctc', 'monthly_basic', 'monthly_hra', 'monthly_ca', 
                    'monthly_sa', 'monthly_employeepf', 'monthly_employerpf', 
                    'monthly_employeeesic', 'monthly_employeresic', 'monthly_gross_salary', 
                    'monthly_newctc', 'monthly_professionalTax', 'monthly_total_deductions', 
                    'monthly_netpay', 'monthly_netpayinwords', 'monthly_incentive', 
                    'monthly_loan_other', 'monthly_presentdays', 'monthly_absentdays', 
                    'monthly_halfdays', 'monthly_unpaiddays', 'monthly_paiddays', 
                    'monthly_weekoffdays']
