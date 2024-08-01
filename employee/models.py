from django.db import models
from hr.models import Company, CompanyBranch, HolidayList, HolidayMaster, Onboarding, candidateResume,WeekOff,Interview
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time

class Department(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Designation(models.Model):
    
    department  =   models.ForeignKey(Department, verbose_name="department", on_delete=models.PROTECT, related_name='designation', default='Select Designations')
    name        =   models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Work_Office(models.Model):
    OFFICE_STATUS = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ]

    office_id   =   models.AutoField( primary_key=True)
    name        =   models.CharField(max_length=255)
    address     =   models.CharField(max_length=255,null=True, blank=True)
    status      =   models.CharField(choices=OFFICE_STATUS, default='Active', max_length=100,null=True, blank=True)
    
    def __str__(self):
        return self.name

    
class Position(models.Model):

    name    =   models.CharField(max_length=255)
    remarks =   models.CharField(max_length=255,null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Gender(models.Model):

    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Employee(models.Model):

    EMPLOYEE_STATUS = [
        ('Active', 'Active'),
        ('Full&Final Pending','Full&Final Pending'),
        ('Deactive', 'Deactive'),
        ]
    EMPLOYEE_MARRIED_STATUS = [
        ('Married', 'Married'),
        ('Unmarried', 'Unmarried'),
        ]
    
    EMPLOYEE_BLOOD_GROUP= [
        ('Not Update', 'Not Update'),
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('AB+','AB+'),
        ('O+', 'O+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('AB-','AB-'),
        ('O-', 'O-'),
        ]
    EMERGENCY_RELATIONAS= [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Spouse', 'Spouse'),
        ('Son','Son'),
        ('Daughter', 'Daughter'),
        ('Other', 'Other'),
    ]

    emp_user                =   models.OneToOneField(User, on_delete=models.PROTECT, related_name='emp_user' ,null=True, blank=True)
    emp_id                  =   models.CharField(max_length=10, primary_key=True)  
    candidate_id            =   models.ForeignKey(candidateResume, on_delete=models.PROTECT)
    first_name              =   models.CharField(max_length=50)
    middle_name             =   models.CharField(max_length=50,blank=True,null=True)
    last_name               =   models.CharField(max_length=50,blank=True,null=True)
    name                    =   models.CharField(max_length=50) # as per aadhaar card 
    gender                  =   models.ForeignKey(Gender, verbose_name="gender",on_delete=models.PROTECT)
    address                 =   models.CharField(max_length=100)#permanent address 
    state                   =   models.CharField(max_length=50) # permanent
    city                    =   models.CharField(max_length=50)#permanent
    country                 =   models.CharField(max_length=50)#permanent
    pin_code                =   models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)#permanent
    c_address               =   models.CharField(max_length=50) #correspondence
    c_state                 =   models.CharField(max_length=50)#correspondence
    c_city                  =   models.CharField(max_length=50)#correspondence
    c_country               =   models.CharField(max_length=50)#correspondence
    c_pin_code              =   models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)#correspondence
    email                   =   models.EmailField(max_length=254, unique=True)
    office_email            =   models.EmailField(max_length=254,blank=True,null=True)
    company_branch          =   models.ForeignKey(CompanyBranch, verbose_name="company_branch",on_delete=models.PROTECT,blank=True,null=True)
    contact_no              =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    other_contact_no        =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    dob                     =   models.DateField(default=timezone.now)
    doj                     =   models.DateField(default=timezone.now)
    doe                     =   models.DateField(blank=True,null=True)
    pfno                    =   models.CharField(max_length=50,blank=True,null=True)
    pf_joining_date         =   models.DateField(blank=True,null=True)
    pf_exit_date            =   models.DateField(blank=True,null=True)
    uanno                   =   models.DecimalField(max_digits=15, decimal_places=0,default=0.0)
    esicno                  =   models.CharField(max_length=50,blank=True,null=True)
    esic_joining_date       =   models.DateField(blank=True,null=True)
    esic_exit_date          =   models.DateField(blank=True,null=True)
    pancard_no              =   models.CharField(max_length=20)
    aadhaarcard_no          =   models.CharField(max_length=20)
    account_no              =   models.DecimalField(max_digits=20,decimal_places=0, null=True, blank=True)
    bank_name               =   models.CharField(max_length=50, null=True, blank=True)
    ifsc_code               =   models.CharField(max_length=50, null=True, blank=True)
    branch                  =   models.CharField(max_length=50, null=True, blank=True) #Bank Branch
    department              =   models.ForeignKey(Department, verbose_name="department",on_delete=models.PROTECT)
    designation             =   models.ForeignKey(Designation, verbose_name="designation",on_delete=models.PROTECT)
    reporting_to            =   models.ForeignKey('self',on_delete=models.SET_NULL,related_name='employees_reporting_to',blank=True,null=True)
    documents_id            =   models.OneToOneField(Onboarding, on_delete=models.PROTECT)
    status                  =   models.CharField(choices=EMPLOYEE_STATUS, default='Deactive', max_length=100,null=True, blank=True)
    interview_take          =   models.BooleanField(default=False)
    reporting_take          =   models.BooleanField(default=False)
    permission_all          =   models.BooleanField(default=False)
    permission_customize    =   models.BooleanField(default=False)
    position                =   models.ForeignKey(Position, verbose_name="position",on_delete=models.PROTECT)
    married_status          =   models.CharField(choices=EMPLOYEE_MARRIED_STATUS, default='Unmarried', max_length=100)
    blood_group             =   models.CharField(choices=EMPLOYEE_BLOOD_GROUP, default='Not Update', max_length=100)
    linkedin_profile        =   models.CharField(max_length=250, null=True, blank=True)
    instagram_profile       =   models.CharField(max_length=250, null=True, blank=True)
    facebook_profile        =   models.CharField(max_length=250, null=True, blank=True)
    password_changed        =   models.BooleanField(default=False)
    esic_apply              =   models.BooleanField(default=False)
    pf_apply                =   models.BooleanField(default=False)
    hr_round                =   models.BooleanField(default=False)
    technical_round         =   models.BooleanField(default=False)
    telephonic_round        =   models.BooleanField(default=False)
    round_two               =   models.BooleanField(default=False)
    round_three             =   models.BooleanField(default=False)
    final_round             =   models.BooleanField(default=False)
    holiday_master          =   models.ForeignKey(HolidayMaster, on_delete=models.PROTECT,null=True, blank=True)
    WeekOff                 =   models.ForeignKey(WeekOff, on_delete=models.PROTECT,null=True, blank=True)
    emergency_contactname   =   models.CharField(max_length=50, null=True, blank=True)
    emergency_contactnumber =   models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
    emergency_relationas    =   models.CharField(choices=EMERGENCY_RELATIONAS, default='Not Update', max_length=100)

    def __str__(self):
        return self.name  

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        
class Attendance(models.Model):
    
    employee        =   models.ForeignKey(Employee, on_delete=models.PROTECT)
    date            =   models.DateField(null=True, blank=True)
    clock_in        =   models.TimeField(null=True, blank=True)
    latitude        =   models.CharField(max_length=50,null=True, blank=True)
    longitude       =   models.CharField(max_length=50,null=True, blank=True)
    clock_out       =   models.TimeField(null=True, blank=True)
    worked_hours    =   models.DurationField(blank=True, null=True)

    is_full_day     =   models.BooleanField(default=False)
    is_half_day     =   models.BooleanField(default=False)
    is_absent       =   models.BooleanField(default=False)
    is_on_leave     =   models.BooleanField(default=False)
    regularized     = models.BooleanField(default=False)
    regularization_requested = models.BooleanField(default=False)
    regularization_approved = models.BooleanField(default=False)
    requested_clock_in = models.TimeField(null=True, blank=True)
    requested_clock_out = models.TimeField(null=True, blank=True)    
    remarks= models.CharField(max_length=100,null=True, blank=True)
    def save(self, from_update=False, *args, **kwargs):
        
        if self.clock_in:
            current_date = datetime.now().date()
            if from_update:
                self.clock_in  = self.clock_in.time()
                self.clock_out = self.clock_out.time()
                clock_in_dt    = datetime.combine(current_date, self.clock_in)
                clock_out_dt   = datetime.combine(current_date, self.clock_out)
            else:
                clock_in_dt = datetime.combine(current_date, self.clock_in)

                if self.clock_out:
                    clock_out_dt = datetime.combine(current_date, self.clock_out)
                else:
                    official_clock_out = datetime.combine(current_date, time(hour=18, minute=0, second=0))
                    clock_out_dt = official_clock_out

            time_worked = clock_out_dt - clock_in_dt

            if time_worked.total_seconds() < 0:
                time_worked = datetime.combine(current_date, time()) - datetime.combine(current_date, time())

            total_hours = time_worked.total_seconds() / 3600

            if total_hours >= 8:
                self.is_full_day = True
                self.is_half_day = False
                self.is_absent   = False
            elif total_hours >= 4:
                self.is_half_day = True
                self.is_full_day = False
                self.is_absent = False
            else:
                self.is_absent = True
                self.is_full_day = False
                self.is_half_day = False

            employee_leave = LeaveApplication.objects.filter(
                employee=self.employee,
                leave_from_date__lte=self.date,
                leave_to_date__gte=self.date,
                leave_status=1
            ).exists()

            if employee_leave:
                leave_instance = LeaveApplication.objects.get(
                    employee=self.employee,
                    leave_from_date__lte=self.date,
                    leave_to_date__gte=self.date,
                    leave_status=1
                )
                leave_from_time = leave_instance.leave_from_time
                leave_to_time = leave_instance.leave_to_time

                if (leave_from_time == time(hour=18, minute=45, second=0) and 
                    leave_to_time == time(hour=10, minute=0, second=0)):
                    if self.clock_in and self.clock_out:
                        clock_in_dt = datetime.combine(current_date, self.clock_in)
                        clock_out_dt = datetime.combine(current_date, self.clock_out)
                        clock_diff_hours = (clock_in_dt - clock_out_dt).seconds / 3600
                        if clock_diff_hours == 4:
                            self.is_full_day = False
                            self.is_half_day = True
                            self.is_absent = False
                            self.is_on_leave = True
            else:
                self.is_on_leave = False

        super(Attendance, self).save(*args, **kwargs)

    @classmethod
    def count_today_clock_ins(cls):
        today = datetime.now().date()
        return cls.objects.filter(date=today, clock_in__isnull=False).count()
    

class LeaveApplication(models.Model):
    LEAVE_STATUS_CHOICES   = (
        (1, 'Approved'),
        (2, 'Pending'),
        (3, 'Rejected'),
    )
    employee         =   models.ForeignKey(Employee, on_delete=models.PROTECT)
    leave_from_date  =   models.DateField()
    leave_from_time  =   models.TimeField()
    leave_to_date    =   models.DateField()
    leave_to_time    =   models.TimeField()
    leave_type       =   models.CharField(max_length=50)
    leave_reason     =   models.TextField()
    leave_status     =   models.IntegerField(choices=LEAVE_STATUS_CHOICES, default=2)
    

class LeaveBalance(models.Model):

    employee     =  models.ForeignKey(Employee, on_delete=models.PROTECT)
    total_leaves =  models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.employee.emp_id 
        
class ResignApplication(models.Model):
    RESIGN_STATUS_CHOICES = (
        (1, 'Approved'),
        (2, 'Pending'),
        (3, 'Rejected'),
    )
    
    employee       =  models.ForeignKey(Employee, on_delete=models.PROTECT)
    resign_date    =  models.DateField()
    last_date      =  models.DateField(default=timezone.now,blank=True,null=True)
    resign_reason  =  models.TextField()
    resign_status  =  models.IntegerField(choices=RESIGN_STATUS_CHOICES, default=2)

