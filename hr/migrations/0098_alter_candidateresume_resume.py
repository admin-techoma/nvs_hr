# Generated by Django 4.2.6 on 2024-08-05 14:39

from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0097_alter_candidateresume_resume_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
