# forms.py
from django import forms
from .models import Payroll,Monthly_salary

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = '__all__'



class MonthlySalaryForm(forms.ModelForm):
    class Meta:
        model = Monthly_salary
        exclude = ['monthly_netpayinwords', 'remarks', 'month', 'year', 'total_full_day', 'total_half_day']
    
     
        
