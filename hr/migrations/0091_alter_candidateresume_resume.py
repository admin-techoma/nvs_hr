# Generated by Django 4.2.6 on 2024-06-24 10:27

from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0090_alter_candidateresume_resume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
