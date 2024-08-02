from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0095_alter_candidateresume_resume_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
        migrations.AlterField(
            model_name='company',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
<<<<<<< HEAD
        migrations.AlterField(
            model_name='interview',
            name='interviewround_status',
            field=models.IntegerField(choices=[(1, 'Complete'), (2, 'Pending'), (3, 'Rejected')], default=2),
        ),
=======
>>>>>>> f7702d5cde0b3a6fffdc1041f8260d8739a7da1c
    ]
