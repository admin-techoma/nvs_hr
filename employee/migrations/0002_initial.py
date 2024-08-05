# Generated by Django 4.2.6 on 2024-08-05 13:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hr', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='WeekOff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr.weekoff'),
        ),
        migrations.AddField(
            model_name='employee',
            name='candidate_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hr.candidateresume'),
        ),
        migrations.AddField(
            model_name='employee',
            name='company_branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr.companybranch', verbose_name='company_branch'),
        ),
        migrations.AddField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.department', verbose_name='department'),
        ),
        migrations.AddField(
            model_name='employee',
            name='designation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.designation', verbose_name='designation'),
        ),
        migrations.AddField(
            model_name='employee',
            name='documents_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='hr.onboarding'),
        ),
        migrations.AddField(
            model_name='employee',
            name='emp_user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='emp_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.gender', verbose_name='gender'),
        ),
        migrations.AddField(
            model_name='employee',
            name='holiday_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr.holidaymaster'),
        ),
        migrations.AddField(
            model_name='employee',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.position', verbose_name='position'),
        ),
        migrations.AddField(
            model_name='employee',
            name='reporting_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees_reporting_to', to='employee.employee'),
        ),
        migrations.AddField(
            model_name='designation',
            name='department',
            field=models.ForeignKey(default='Select Designations', on_delete=django.db.models.deletion.PROTECT, related_name='designation', to='employee.department', verbose_name='department'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee.employee'),
        ),
    ]
