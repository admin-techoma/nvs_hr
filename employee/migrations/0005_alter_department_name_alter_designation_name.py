# Generated by Django 4.2.6 on 2024-04-30 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_alter_employee_married_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='designation',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
