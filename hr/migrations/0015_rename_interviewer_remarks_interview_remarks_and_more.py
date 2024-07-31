# Generated by Django 5.0 on 2024-03-20 10:30

import hr.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0014_alter_candidateresume_resume'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interview',
            old_name='interviewer_remarks',
            new_name='remarks',
        ),
        migrations.AddField(
            model_name='interview',
            name='interviewround_status',
            field=models.IntegerField(choices=[(1, 'Approved'), (2, 'Pending'), (3, 'Rejected')], default=2),
        ),
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
