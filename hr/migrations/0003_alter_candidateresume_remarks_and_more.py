# Generated by Django 4.2.6 on 2024-08-07 10:29

from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0002_alter_candidateresume_resume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='remarks',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
