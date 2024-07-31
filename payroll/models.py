from django.db import models
from datetime import timezone
from django.utils import timezone
from employee.models import Attendance, Employee

# Create your models here.
class Payroll(models.Model):
   
    PAYROLL_STATUS = [
    ('Active', 'Active'),
    ('Deactive', 'Deactive'),
    ]
    PAYMENT_MODE = [
    ('Bank Transfer', 'Bank Transfer'),
    ('Cheque', 'Cheque'),
    ('Cash', 'Cash'),
    ]
    payroll_id          =    models.CharField(max_length=10, primary_key =True)  
    emp_id              =    models.ForeignKey(Employee, on_delete=models.PROTECT)
    ctc                 =    models.FloatField(verbose_name="ctc",blank=True,null=True,default=0)
    basic               =    models.FloatField(verbose_name="basic",blank=True,null=True,default=0)
    hra                 =    models.FloatField(verbose_name="hra",blank=True,null=True,default=0)
    ca                  =    models.FloatField(verbose_name="conviction",blank=True,null=True,default=0)
    sa                  =    models.FloatField(verbose_name="special_allowance",blank=True,null=True,default=0)
    employee_pf         =    models.FloatField(verbose_name="EmployeePF",blank=True,null=True,default=0)
    employer_pf         =    models.FloatField(verbose_name="EmployerPF",blank=True,null=True,default=0)
    employee_esic       =    models.FloatField(verbose_name="EmployeeESIC",blank=True,null=True,default=0)
    employer_esic       =    models.FloatField(verbose_name="EmployerESIC",blank=True,null=True,default=0)
    pt                  =    models.FloatField(verbose_name="PT",blank=True,null=True,default=0)
    gmc                 =    models.FloatField(verbose_name="gmc",blank=True,null=True,default=0)
    tds                 =    models.FloatField(verbose_name="tds",blank=True,null=True,default=0)
    vpf                 =    models.FloatField(verbose_name="vpf",blank=True,null=True,default=0)
    gross_salary        =    models.FloatField(verbose_name="gross_salary",blank=True,null=True,default=0)
    total_deduction     =    models.FloatField(verbose_name="total_deduction",blank=True,null=True,default=0)
    net_salary          =    models.FloatField(verbose_name="net_salary",blank=True,null=True,default=0)
    gratuity            =    models.FloatField(verbose_name="gratuity",blank=True,null=True,default=0)
    otherone            =    models.FloatField(verbose_name="otherone",blank=True,null=True,default=0)
    monthly_ctc         =    models.FloatField(verbose_name="monthly_ctc",blank=True,null=True,default=0)
    payment_cycle       =    models.FloatField(verbose_name="payment_cycle",blank=True,null=True,default=0)
    applicable_from     =    models.DateField(default=timezone.now)
    remarks             =    models.CharField(max_length=500,verbose_name="remarks",blank=True,null=True)
    status              =    models.CharField(choices=PAYROLL_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    paymentmode         =    models.CharField(choices=PAYMENT_MODE, default='Bank Transfer', max_length=100,null=True, blank=True)
    yearlyctc           =    models.FloatField(verbose_name="yearlyctc",blank=True,null=True,default=0)
    
    def __str__(self):
        return self.payroll_id
    
class Monthly_salary(models.Model):
    PAYMENT_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    
    payroll_id              =   models.CharField(max_length=20, blank=True, null=True)
    emp_id                  =   models.ForeignKey(Employee, on_delete=models.PROTECT)
    month                   =   models.CharField(max_length=255)
    year                    =   models.CharField(max_length=255)
    salary_createdon        =   models.DateTimeField(db_column='salary_createdon', blank=True, null=True, default=timezone.now)
    payment_status          =   models.CharField(choices=PAYMENT_STATUS, default='Paid', max_length=100, null=True, blank=True)
    remarks                 =   models.CharField(max_length=250, blank=True, null=True)
    name                    =   models.CharField(max_length=255, blank=True, null=True)
    email                   =   models.CharField(max_length=255, blank=True, null=True)
    # Fixed Fields      
    fixed_ctc               =   models.FloatField(verbose_name="fixed_ctc", blank=True, null=True, default=0)
    fixed_basic             =   models.FloatField(verbose_name="fixed_basic", blank=True, null=True, default=0)
    fixed_hra               =   models.FloatField(verbose_name="fixed_hra", blank=True, null=True, default=0)
    fixed_ca                =   models.FloatField(verbose_name="fixed_ca", blank=True, null=True, default=0)
    fixed_sa                =   models.FloatField(verbose_name="fixed_sa", blank=True, null=True, default=0)
    fixed_employeepf        =   models.FloatField(verbose_name="fixed_employeepf", blank=True, null=True, default=0)
    fixed_employerpf        =   models.FloatField(verbose_name="fixed_employerpf", blank=True, null=True, default=0)
    fixed_employeeesic      =   models.FloatField(verbose_name="fixed_employeeesic", blank=True, null=True, default=0)
    fixed_employeresic      =   models.FloatField(verbose_name="fixed_employeresic", blank=True, null=True, default=0)
    fixed_gross_salary      =   models.FloatField(verbose_name="fixed_gross_salary", blank=True, null=True, default=0)
    fixed_newctc            =   models.FloatField(verbose_name="fixed_newctc", blank=True, null=True, default=0)
    fixed_professionalTax   =   models.FloatField(verbose_name="fixed_professionalTax", blank=True, null=True, default=0)
    fixed_total_deducation  =   models.FloatField(verbose_name="fixed_total_deducation", blank=True, null=True, default=0)
    fixed_netpay            =   models.FloatField(verbose_name="fixed_netpay", blank=True, null=True, default=0)
    # Monthly Fields    
    monthly_ctc             =   models.FloatField(verbose_name="monthly_ctc", default=0)
    monthly_basic           =   models.FloatField(verbose_name="monthly_basic", default=0)
    monthly_hra             =   models.FloatField(verbose_name="monthly_hra", default=0)
    monthly_ca              =   models.FloatField(verbose_name="monthly_ca", default=0)
    monthly_sa              =   models.FloatField(verbose_name="monthly_sa", default=0)
    monthly_employeepf      =   models.FloatField(verbose_name="monthly_employeepf", default=0)
    monthly_employerpf      =   models.FloatField(verbose_name="monthly_employerpf", default=0)
    monthly_employeeesic    =   models.FloatField(verbose_name="monthly_employeeesic", default=0)
    monthly_employeresic    =   models.FloatField(verbose_name="monthly_employeresic", default=0)
    monthly_gross_salary    =   models.FloatField(verbose_name="monthly_gross_salary", default=0)
    monthly_newctc          =   models.FloatField(verbose_name="monthly_newctc", default=0)
    monthly_professionalTax =   models.FloatField(verbose_name="monthly_professionalTax", default=0)
    monthly_total_deductions=   models.FloatField(verbose_name="monthly_total_deductions", default=0)
    monthly_netpay          =   models.FloatField(verbose_name="monthly_netpay",  default=0)
    monthly_netpayinwords   =   models.CharField(max_length=250,blank=True, null=True)
    monthly_incentive       =   models.FloatField(verbose_name="monthly_incentive",default=0)
    monthly_loan_other      =   models.FloatField(verbose_name="monthly_loan_other", default=0)
    monthly_presentdays     =   models.FloatField(verbose_name="presentday", blank=True, null=True, default=0)
    monthly_absentdays      =   models.FloatField(verbose_name="absentday", blank=True, null=True, default=0)
    monthly_halfdays        =   models.FloatField(verbose_name="halfdays", blank=True, null=True, default=0)
    monthly_unpaiddays      =   models.FloatField(verbose_name="unpaidday", blank=True, null=True, default=0)
    monthly_paiddays        =   models.FloatField(verbose_name="paidday", blank=True, null=True, default=0)
    monthly_weekoffdays     =   models.FloatField(verbose_name="weekoff", blank=True, null=True, default=0)
    