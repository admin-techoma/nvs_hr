# Generated by Django 5.0 on 2024-03-01 10:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monthly_salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payroll_id', models.CharField(blank=True, max_length=20, null=True)),
                ('emp_id', models.CharField(blank=True, max_length=20, null=True)),
                ('month', models.CharField(max_length=255)),
                ('year', models.CharField(max_length=255)),
                ('salary_createdon', models.DateTimeField(blank=True, db_column='salary_createdon', default=django.utils.timezone.now, null=True)),
                ('payment_status', models.CharField(blank=True, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Paid', max_length=100, null=True)),
                ('remarks', models.CharField(blank=True, max_length=250, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('fixed_ctc', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_ctc')),
                ('fixed_basic', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_basic')),
                ('fixed_hra', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_hra')),
                ('fixed_ca', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_ca')),
                ('fixed_sa', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_sa')),
                ('fixed_employeepf', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_employeepf')),
                ('fixed_employerpf', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_employerpf')),
                ('fixed_employeeesic', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_employeeesic')),
                ('fixed_employeresic', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_employeresic')),
                ('fixed_gross_salary', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_gross_salary')),
                ('fixed_newctc', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_newctc')),
                ('fixed_professionalTax', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_professionalTax')),
                ('fixed_total_deducation', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_total_deducation')),
                ('fixed_netpay', models.FloatField(blank=True, default=0, null=True, verbose_name='fixed_netpay')),
                ('monthly_ctc', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_ctc')),
                ('monthly_basic', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_basic')),
                ('monthly_hra', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_hra')),
                ('monthly_ca', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_ca')),
                ('monthly_sa', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_sa')),
                ('monthly_employeepf', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_employeepf')),
                ('monthly_employerpf', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_employerpf')),
                ('monthly_employeeesic', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_employeeesic')),
                ('monthly_employeresic', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_employeresic')),
                ('monthly_gross_salary', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_gross_salary')),
                ('monthly_newctc', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_newctc')),
                ('monthly_professionalTax', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_professionalTax')),
                ('monthly_total_deductions', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_total_deductions')),
                ('monthly_netpay', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_netpay')),
                ('monthly_netpayinwords', models.CharField(max_length=250)),
                ('monthly_incentive', models.FloatField(default=0, verbose_name='incentive')),
                ('monthly_loan_other', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_loan_other')),
                ('monthly_presentdays', models.FloatField(blank=True, default=0, null=True, verbose_name='presentday')),
                ('monthly_absentdays', models.FloatField(blank=True, default=0, null=True, verbose_name='absentday')),
                ('monthly_halfdays', models.FloatField(blank=True, default=0, null=True, verbose_name='halfdays')),
                ('monthly_unpaiddays', models.FloatField(blank=True, default=0, null=True, verbose_name='unpaidday')),
                ('monthly_paiddays', models.FloatField(blank=True, default=0, null=True, verbose_name='paidday')),
                ('monthly_weekoffdays', models.FloatField(blank=True, default=0, null=True, verbose_name='weekoff')),
            ],
        ),
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('payroll_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('ctc', models.FloatField(blank=True, default=0, null=True, verbose_name='ctc')),
                ('basic', models.FloatField(blank=True, default=0, null=True, verbose_name='basic')),
                ('hra', models.FloatField(blank=True, default=0, null=True, verbose_name='hra')),
                ('ca', models.FloatField(blank=True, default=0, null=True, verbose_name='conviction')),
                ('sa', models.FloatField(blank=True, default=0, null=True, verbose_name='special_allowance')),
                ('employee_pf', models.FloatField(blank=True, default=0, null=True, verbose_name='EmployeePF')),
                ('employer_pf', models.FloatField(blank=True, default=0, null=True, verbose_name='EmployerPF')),
                ('employee_esic', models.FloatField(blank=True, default=0, null=True, verbose_name='EmployeeESIC')),
                ('employer_esic', models.FloatField(blank=True, default=0, null=True, verbose_name='EmployerESIC')),
                ('pt', models.FloatField(blank=True, default=0, null=True, verbose_name='PT')),
                ('gmc', models.FloatField(blank=True, default=0, null=True, verbose_name='gmc')),
                ('tds', models.FloatField(blank=True, default=0, null=True, verbose_name='tds')),
                ('vpf', models.FloatField(blank=True, default=0, null=True, verbose_name='vpf')),
                ('gross_salary', models.FloatField(blank=True, default=0, null=True, verbose_name='gross_salary')),
                ('total_deduction', models.FloatField(blank=True, default=0, null=True, verbose_name='total_deduction')),
                ('net_salary', models.FloatField(blank=True, default=0, null=True, verbose_name='net_salary')),
                ('gratuity', models.FloatField(blank=True, default=0, null=True, verbose_name='gratuity')),
                ('otherone', models.FloatField(blank=True, default=0, null=True, verbose_name='otherone')),
                ('monthly_ctc', models.FloatField(blank=True, default=0, null=True, verbose_name='monthly_ctc')),
                ('payment_cycle', models.FloatField(blank=True, default=0, null=True, verbose_name='payment_cycle')),
                ('applicable_from', models.DateField(default=django.utils.timezone.now)),
                ('remarks', models.FloatField(blank=True, default=0, null=True, verbose_name='remarks')),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Deactive', 'Deactive')], default='Deactive', max_length=100, null=True)),
                ('paymentmode', models.CharField(blank=True, choices=[('Bank Transfer', 'Bank Transfer'), ('Cheque', 'Cheque'), ('Cash', 'Cash')], default='Bank Transfer', max_length=100, null=True)),
                ('yearlyctc', models.FloatField(blank=True, default=0, null=True, verbose_name='yearlyctc')),
                ('emp_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
        ),
    ]
