# Generated by Django 4.2.6 on 2024-06-21 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0008_alter_monthly_salary_monthly_basic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthly_salary',
            name='monthly_incentive',
            field=models.FloatField(default=0, verbose_name='monthly_incentive'),
        ),
    ]
