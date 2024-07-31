from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db import models
from django.utils import timezone

# from employee.models import Department,Designation

logger = get_task_logger(__name__)

@shared_task
def scheduled_task():
    try:
        # Import the ResignApplication model here to avoid circular import
        from employee.models import ResignApplication

        timezone.activate(timezone.get_current_timezone())
        logger.info("Scheduled task started at {}".format(timezone.now()))

        current_datetime = timezone.now()

        # Check resign applications with status 'Approved'
        approved_resignations = ResignApplication.objects.filter(
            resign_status=1,
            last_date__lte=current_datetime,  # Use '__lte' to filter based on less than or equal to the current datetime
        )

        for resignation in approved_resignations:
            employee = resignation.employee

            # Check if today's date is the next day of the last date
            if current_datetime.date() == resignation.last_date:
                # Update user model
                employee.emp_user.is_active = False
                employee.emp_user.save()

                # Update employee model
                employee.status = 'Full&Final Pending'
                employee.save()

                logger.info(f"Updated user {employee.emp_user.username} and employee {employee.name}")
    except Exception as e:
        logger.error("Error in scheduled task: {}".format(e))


def resume_upload_path(instance, filename):
    # Define the upload path for the resume files
    return f'hr/Resumes/{filename}'

class candidateResume(models.Model):
    
    candidate_id            =  models.AutoField(primary_key=True)
    name                    =  models.CharField(max_length=255)
    phone_number            =  models.PositiveIntegerField()
    email                   =  models.EmailField()
    resume                  =  models.FileField(upload_to=resume_upload_path)
    remarks                 =  models.TextField()
    status                  =  models.CharField(max_length=20,choices=[('Pending', 'Pending'),('Shortlisted', 'Shortlisted'),('Rejected', 'Rejected'),('Close', 'Close'),('On hold', 'On hold')],default='Pending')
    created_at              =  models.DateTimeField(default=timezone.now, editable=False)
    Exp                     =  models.FloatField(null=True)
    department              =  models.ForeignKey('employee.Department', verbose_name="department", on_delete=models.PROTECT, default=None, null=True)
    designation             =  models.ForeignKey('employee.Designation', verbose_name="designation", on_delete=models.PROTECT, default=None, null=True)
    interviewFeedback       =  models.CharField(max_length=20,choices=[('Pending', 'Pending'),('On-Hold', 'On-Hold'),('Selected', 'Selected'),('Rejected', 'Rejected'),('IsEmployeeNow', 'IsEmployeeNow'),],default='Pending')
    interviewFeedback_date  =  models.DateField(blank=True, null=True)
    
    department_model = None
    designation_model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import models dynamically when needed
        self.department_model = apps.get_model('employee', 'Department')
        self.designation_model = apps.get_model('employee', 'Designation')

    def __str__(self):  
        return self.name

class Interview(models.Model):
    INTERVIEWROUND_STATUS = (
        (1, 'Select'),
        (2, 'Pending'),
        (3, 'Rejected'),
        )
    
    candidate_id            =  models.ForeignKey(candidateResume, on_delete=models.PROTECT)
    department              =  models.ForeignKey('employee.Department', verbose_name="Department", on_delete=models.PROTECT, default=None, null=True)
    designation             =  models.ForeignKey('employee.Designation', verbose_name="Designation", on_delete=models.PROTECT, default=None, null=True)
    interviewMode           =  models.CharField(max_length=20,choices=[('', 'Select')] + [('Online', 'Online'),('Face to Face', 'Face to Face'),])
    interviewer             =  models.CharField(max_length=255)
    interviewRound          =  models.CharField(max_length=20,choices= [('Telephonic Round', 'Telephonic Round'),('HR Round', 'HR Round'),('Technical Round', 'Technical Round'),('Round Two', 'Round Two'),('Round Three', 'Round Three'),('Final Round', 'Final Round'),])
    interviewDate           =  models.DateField()
    interviewTime           =  models.TimeField()
    interviewround_remarks  =  models.CharField(max_length=255)
    interviewround_status   =  models.IntegerField(choices=INTERVIEWROUND_STATUS, default=2)
    
    def __str__(self):
        return self.candidate_id.name



def resume_upload_path(instance, filename):
    # Define the upload path for the resume files
    return f'hr/Onboarding/{filename}'

class Onboarding(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('kyc_complete', 'KYC Complete'),
    ]

    doc_id                    =   models.AutoField(primary_key=True)
    candidate_id              =   models.ForeignKey(candidateResume, on_delete=models.PROTECT)
    c_psimg                   =   models.FileField(upload_to='resume_upload_path', default='/resume_upload_path/avtar.jpg')
    c_adhar                   =   models.FileField(upload_to='resume_upload_path')
    c_pan                     =   models.FileField(upload_to='resume_upload_path')
    c_bankDetails             =   models.FileField(upload_to='resume_upload_path') # cancel cheque
    c_bankStatement           =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_salarySlips             =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_expLetter               =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_previousJoiningLetter   =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_degree                  =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_masters                 =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_HSC                     =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_SSC                     =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    c_otherCertificate        =   models.FileField(upload_to='resume_upload_path', null=True, blank=True)
    status                    =   models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def update_status(self):
        # Check if all required four documents exist
        required_documents = ['c_psimg', 'c_adhar', 'c_pan', 'c_bankDetails']

        for document in required_documents:
            if getattr(self, document) is None:
                self.status = 'pending'
                return

        # Check if all documents exist (including the required four)
        all_documents = [
            'c_psimg', 'c_adhar', 'c_pan', 'c_bankDetails',
            'c_bankStatement', 'c_salarySlips', 'c_expLetter',
            'c_previousJoiningLetter', 'c_degree', 'c_masters',
            'c_HSC', 'c_SSC', 'c_otherCertificate'
        ]

        for document in all_documents:
            if getattr(self, document) is None:
                self.status = 'kyc_complete'
                return

        # If all documents exist, set status to complete
        self.status = 'pending'

    def save(self, *args, **kwargs):
        # Update status before saving
        self.update_status()
        super().save(*args, **kwargs)



class HolidayMaster(models.Model):

    year    =   models.DateField(max_length=10)
    name    =   models.CharField(max_length=100)
    remarks =   models.CharField(max_length=100)

    def __str__(self):
        return self.name

class HolidayList(models.Model):
    holiday_master  =   models.ForeignKey(HolidayMaster,on_delete=models.PROTECT)
    date            =   models.DateField(max_length=10)
    festival_name   =   models.CharField(max_length=100)


    def __str__(self):
        return f"{self.date} - {self.festival_name}"


def logo_upload_path(instance, filename):
    # Define the upload path for the logos files
    return f'hr/Company/{filename}'

def company_document_upload_path(instance, filename):
    # Define the upload path for the logos files
    return f'hr/Company/{filename}'


class Company(models.Model):

    COMPANY_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]

    name                    =      models.CharField(max_length=100)
    
    phone_no                =      models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    website                 =      models.CharField(max_length=100,blank=True,null=True)
    domain                  =      models.CharField(max_length=100,blank=True,null=True)
    email_id                =      models.EmailField(max_length=254, unique=True,blank=True,null=True)
    
    industries_type         =      models.CharField(max_length=100,blank=True,null=True)
    logo                    =      models.FileField(upload_to='logo_upload_path', null=True, blank=True)
    
    reg_address             =      models.CharField(max_length=100,blank=True,null=True) 
    reg_city                =      models.CharField(max_length=100,blank=True,null=True)
    reg_state               =      models.CharField(max_length=100,blank=True,null=True)
    reg_country             =      models.CharField(max_length=100,blank=True,null=True)
    reg_pin_code            =      models.CharField(max_length=100,blank=True,null=True)

    corp_address            =      models.CharField(max_length=100,blank=True,null=True) 
    corp_city               =      models.CharField(max_length=100,blank=True,null=True)
    corp_state              =      models.CharField(max_length=100,blank=True,null=True)
    corp_country            =      models.CharField(max_length=100,blank=True,null=True)
    corp_pin_code           =      models.CharField(max_length=100,blank=True,null=True)

    gst_no                  =      models.CharField(max_length=15,blank=True,null=True)
    tin_no                  =      models.CharField(max_length=15,blank=True,null=True)
    cin_no                  =      models.CharField(max_length=25,blank=True,null=True)
    pancard_no              =      models.CharField(max_length=20,blank=True,null=True)
    aadhaarcard_no          =      models.CharField(max_length=20,blank=True,null=True)
    account_no              =      models.DecimalField(max_digits=20,decimal_places=0, null=True, blank=True)
    bank_name               =      models.CharField(max_length=50, null=True, blank=True)
    ifsc_code               =      models.CharField(max_length=50, null=True, blank=True)
    branch                  =      models.CharField(max_length=50, null=True, blank=True) #Bank Branch
    start_date              =      models.DateField(max_length=10,blank=True,null=True)
    end_date                =      models.DateField(max_length=10,blank=True,null=True)
    status                  =      models.CharField(choices=COMPANY_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    document                =      models.FileField(upload_to='company_document_upload_path', null=True, blank=True)
    emp_id_series           =      models.CharField(max_length=100,blank=True,null=True)
    def __str__(self):
        return self.name

class CompanyBankDetails(models.Model):
    COMPANY_BANK_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]
    
    company         =   models.ForeignKey(Company, verbose_name="company", on_delete=models.PROTECT, related_name='company_bank', default='Select Company Bank')
    bank_name       =   models.CharField(max_length=255,null=True)
    ifsc_code       =   models.CharField(max_length=255,null=True)
    branch          =   models.CharField(max_length=255,null=True)
    account_no      =   models.DecimalField(max_digits=25,decimal_places=0)
    remarks         =   models.CharField(max_length=255,null=True)
    status          =   models.CharField(choices=COMPANY_BANK_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    def __str__(self):
        return self.bank_name

class CompanyBranch(models.Model):
    COMPANY_BRANCH_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]


    company         =   models.ForeignKey(Company, verbose_name="company", on_delete=models.PROTECT, related_name='company_branch', default='Select Company Branch')
    name            =   models.CharField(max_length=255,null=True)
    address         =   models.CharField(max_length=100)#permanent address 
    state           =   models.CharField(max_length=50) # permanent
    city            =   models.CharField(max_length=50)#permanent
    country         =   models.CharField(max_length=50)#permanent
    pin_code        =   models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)#permanent
    email           =   models.EmailField(max_length=254, unique=True)
    contact_no      =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    start_date      =  models.DateField(max_length=10,blank=True,null=True)
    end_date        =   models.DateField(max_length=10,blank=True,null=True)
    status          =   models.CharField(choices=COMPANY_BRANCH_STATUS, default='Deactive', max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name

class ShiftMaster(models.Model):

    name        =   models.CharField(max_length=100,blank=True,null=True)
    start_time  =   models.TimeField()
    end_time    =   models.TimeField()

def company_Announcement_postupload_path(instance, filename):
    # Define the upload path for the logos files
    return f'hr/Company/{filename}'

class Announcement(models.Model):
    COMPANY_ANNOUNCEMENTS_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]


    company     =   models.ForeignKey(Company, verbose_name="company", on_delete=models.PROTECT, related_name='company_announcement', null=True, blank=True)
    name        =   models.CharField(max_length=100)
    created_on  =   models.DateField(max_length=10)
    message     =   models.CharField(max_length=100)
    file        =   models.FileField(upload_to='company_Announcement_postupload_path', null=True, blank=True)
    status      =   models.CharField(choices=COMPANY_ANNOUNCEMENTS_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    
    def __str__(self):
        return self.name
    

def company_Policies_upload_path(instance, filename):
    # Define the upload path for the logos files
    return f'hr/Company/{filename}'

class Policies(models.Model):
    COMPANY_POLICY_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]


    company    =   models.ForeignKey(Company, verbose_name="company", on_delete=models.PROTECT, related_name='company_policy', null=True, blank=True)
    name       =   models.CharField(max_length=100)
    created_on =   models.DateField(max_length=10)
    remarks    =   models.CharField(max_length=100)
    file       =   models.FileField(upload_to='company_Policies_upload_path', null=True, blank=True)
    status     =   models.CharField(choices=COMPANY_POLICY_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    def __str__(self):
        return self.name
    

class WeekOff(models.Model):
    name       =   models.CharField(max_length=100)
    remarks    =   models.CharField(max_length=100)

    def __str__(self):
        return self.name    
    
class WeekOffNo(models.Model):
    WEEKOFF_NO= [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        ]
    
    weekoff     =   models.ForeignKey(WeekOff, verbose_name="Week Off", on_delete=models.PROTECT, related_name='weekoff_nos', default='Select Weekoff_nos')
    week_no     =   models.CharField(choices=WEEKOFF_NO, default='1', max_length=2)

    
    def __str__(self):
        return self.week_no 



class WeekOffDay(models.Model):
    WEEKOFF_DAY= [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
       

        ]
    WEEKOFF_DAY_VALUE= [
        (0, 'Half Day'),
        (1, 'Full Day'),
        (2, 'Off'),
       
        ]
    week_no     =   models.ForeignKey(WeekOffNo, verbose_name="Week No", on_delete=models.CASCADE, related_name='weekoff_day', default='0')
    week_day    =   models.CharField(choices=WEEKOFF_DAY, default=0, max_length=10)
    week_value  =   models.CharField(choices=WEEKOFF_DAY_VALUE, default=0, max_length=10)
    
    
    def __str__(self):
        return self.week_day
    


class CompanyPayrollDetails(models.Model):
    
    company         =   models.ForeignKey(Company, verbose_name="CompanyPayrollDetails", on_delete=models.PROTECT, related_name='company_payroll', default='Select Company Payroll')
    basic           =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    hra             =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    ca              =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True) #Conviction Allowance
    sa              =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True) #Special Allowance
    pt              =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True) #Professional Tax
    employer_pf     =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    employer_esic   =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    employee_pf     =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    employee_esic   =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
