# Generated by Django 4.2.6 on 2024-08-05 16:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('clock_in', models.TimeField(blank=True, null=True)),
                ('latitude', models.CharField(blank=True, max_length=50, null=True)),
                ('longitude', models.CharField(blank=True, max_length=50, null=True)),
                ('clock_out', models.TimeField(blank=True, null=True)),
                ('worked_hours', models.DurationField(blank=True, null=True)),
                ('is_full_day', models.BooleanField(default=False)),
                ('is_half_day', models.BooleanField(default=False)),
                ('is_absent', models.BooleanField(default=False)),
                ('is_on_leave', models.BooleanField(default=False)),
                ('regularized', models.BooleanField(default=False)),
                ('regularization_requested', models.BooleanField(default=False)),
                ('regularization_approved', models.BooleanField(default=False)),
                ('requested_clock_in', models.TimeField(blank=True, null=True)),
                ('requested_clock_out', models.TimeField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('emp_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('pin_code', models.DecimalField(blank=True, decimal_places=0, max_digits=6, null=True)),
                ('c_address', models.CharField(max_length=50)),
                ('c_state', models.CharField(max_length=50)),
                ('c_city', models.CharField(max_length=50)),
                ('c_country', models.CharField(max_length=50)),
                ('c_pin_code', models.DecimalField(blank=True, decimal_places=0, max_digits=6, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('office_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('contact_no', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('other_contact_no', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('dob', models.DateField(default=django.utils.timezone.now)),
                ('doj', models.DateField(default=django.utils.timezone.now)),
                ('doe', models.DateField(blank=True, null=True)),
                ('pfno', models.CharField(blank=True, max_length=50, null=True)),
                ('pf_joining_date', models.DateField(blank=True, null=True)),
                ('pf_exit_date', models.DateField(blank=True, null=True)),
                ('uanno', models.DecimalField(decimal_places=0, default=0.0, max_digits=15)),
                ('esicno', models.CharField(blank=True, max_length=50, null=True)),
                ('esic_joining_date', models.DateField(blank=True, null=True)),
                ('esic_exit_date', models.DateField(blank=True, null=True)),
                ('pancard_no', models.CharField(max_length=20)),
                ('aadhaarcard_no', models.CharField(max_length=20)),
                ('account_no', models.DecimalField(blank=True, decimal_places=0, max_digits=20, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=50, null=True)),
                ('ifsc_code', models.CharField(blank=True, max_length=50, null=True)),
                ('branch', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Full&Final Pending', 'Full&Final Pending'), ('Deactive', 'Deactive')], default='Deactive', max_length=100, null=True)),
                ('reporting_take', models.BooleanField(default=False)),
                ('married_status', models.CharField(choices=[('Married', 'Married'), ('Unmarried', 'Unmarried')], default='Unmarried', max_length=100)),
                ('blood_group', models.CharField(choices=[('Not Update', 'Not Update'), ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'), ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-')], default='Not Update', max_length=100)),
                ('linkedin_profile', models.CharField(blank=True, max_length=250, null=True)),
                ('instagram_profile', models.CharField(blank=True, max_length=250, null=True)),
                ('facebook_profile', models.CharField(blank=True, max_length=250, null=True)),
                ('password_changed', models.BooleanField(default=False)),
                ('emergency_contactname', models.CharField(blank=True, max_length=50, null=True)),
                ('emergency_contactnumber', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('emergency_relationas', models.CharField(choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Spouse', 'Spouse'), ('Son', 'Son'), ('Daughter', 'Daughter'), ('Other', 'Other')], default='Not Update', max_length=100)),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('remarks', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Work_Office',
            fields=[
                ('office_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Deactive', 'Deactive')], default='Active', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResignApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resign_date', models.DateField()),
                ('last_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('resign_reason', models.TextField()),
                ('resign_status', models.IntegerField(choices=[(1, 'Approved'), (2, 'Pending'), (3, 'Rejected')], default=2)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_leaves', models.PositiveIntegerField(default=0)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_from_date', models.DateField()),
                ('leave_from_time', models.TimeField()),
                ('leave_to_date', models.DateField()),
                ('leave_to_time', models.TimeField()),
                ('leave_type', models.CharField(max_length=50)),
                ('leave_reason', models.TextField()),
                ('leave_status', models.IntegerField(choices=[(1, 'Approved'), (2, 'Pending'), (3, 'Rejected')], default=2)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.employee')),
            ],
        ),
    ]
