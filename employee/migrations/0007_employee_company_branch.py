# Generated by Django 4.2.6 on 2024-05-17 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0068_alter_candidateresume_resume'),
        ('employee', '0006_alter_attendance_employee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='company_branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr.companybranch', verbose_name='company_branch'),
        ),
    ]
