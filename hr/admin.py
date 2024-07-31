from django.contrib import admin
from .models import Policies,Announcement , CompanyBankDetails,candidateResume, Interview, Onboarding, HolidayMaster, HolidayList, Company, ShiftMaster, CompanyBranch, WeekOff, WeekOffNo, WeekOffDay, CompanyPayrollDetails

@admin.register(candidateResume)
class candidateResume(admin.ModelAdmin):
    list_display=[id, 'candidate_id', 'name', 'phone_number', 'email','status']

@admin.register(Interview)
class Interview(admin.ModelAdmin):
    list_display=[id, 'candidate_id', 'interviewMode', 'interviewRound', 'interviewDate','interviewTime','interviewround_remarks','interviewround_status']

@admin.register(Onboarding)
class Onboarding(admin.ModelAdmin):
    list_display=['doc_id', 'candidate_id_id', 'candidate_id']

@admin.register(HolidayMaster)
class HolidayMaster(admin.ModelAdmin):
    list_display=['year', 'name', 'remarks']

@admin.register(HolidayList)
class HolidayList(admin.ModelAdmin):
    list_display=['holiday_master', 'date', 'festival_name']


@admin.register(Company)
class Company(admin.ModelAdmin):
    list_display=['name', 'start_date', 'status']

@admin.register(CompanyBranch)
class CompanyBranch(admin.ModelAdmin):
    list_display=['company','name', 'status']

@admin.register(CompanyBankDetails)
class CompanyBankDetails(admin.ModelAdmin):
    list_display=['company','bank_name','account_no', 'status']    

@admin.register(ShiftMaster)
class ShiftMaster(admin.ModelAdmin):
    list_display=['name', 'start_time', 'end_time']


@admin.register(Announcement)
class Announcement(admin.ModelAdmin):
    list_display=['name', 'created_on', 'message']

@admin.register(Policies)
class Policies(admin.ModelAdmin):
    list_display=['name', 'created_on', 'remarks']    

@admin.register(WeekOff)
class WeekOff(admin.ModelAdmin):
    list_display=['name', 'remarks']    

@admin.register(WeekOffNo)
class WeekOffNo(admin.ModelAdmin):
    list_display=['weekoff', 'week_no']    

@admin.register(WeekOffDay)
class WeekOffDay(admin.ModelAdmin):
    list_display=['week_no', 'week_day', 'week_value']    

@admin.register(CompanyPayrollDetails)
class CompanyPayrollDetails(admin.ModelAdmin):
    list_display=['basic', 'hra','ca','sa','pt','employer_pf','employer_esic','employee_pf','employee_esic']