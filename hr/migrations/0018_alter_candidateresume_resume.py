# Generated by Django 5.0 on 2024-03-27 11:15

import hr.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0017_candidateresume_interviewfeedback_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
