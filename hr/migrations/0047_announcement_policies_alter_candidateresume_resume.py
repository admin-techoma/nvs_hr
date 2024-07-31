# Generated by Django 4.2.6 on 2024-05-06 09:16

from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0046_alter_candidateresume_resume'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField()),
                ('message', models.CharField(max_length=100)),
                ('file', models.FileField(blank=True, null=True, upload_to='company_Announcement_postupload_path')),
            ],
        ),
        migrations.CreateModel(
            name='Policies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField()),
                ('remarks', models.CharField(max_length=100)),
                ('file', models.FileField(blank=True, null=True, upload_to='company_Policies_upload_path')),
            ],
        ),
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
    ]
