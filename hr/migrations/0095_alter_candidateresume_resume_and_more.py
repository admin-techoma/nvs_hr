
from django.db import migrations, models
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0094_alter_candidateresume_resume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresume',
            name='resume',
            field=models.FileField(upload_to=hr.models.resume_upload_path),
        ),
        migrations.AlterField(
            model_name='onboarding',
            name='c_psimg',
            field=models.FileField(default='/resume_upload_path/avtar.jpg', upload_to='resume_upload_path'),
        ),
    ]
