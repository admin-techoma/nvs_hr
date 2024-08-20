from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Policies, Announcement, CompanyBankDetails, candidateResume, Interview, Onboarding, HolidayMaster, HolidayList, Company, ShiftMaster, CompanyBranch, WeekOff, WeekOffNo, WeekOffDay, CompanyPayrollDetails

# Define Resource classes for each model (if needed for custom import/export)
class CandidateResumeResource(resources.ModelResource):
    class Meta:
        model = candidateResume
        import_id_fields = ['candidate_id']

class InterviewResource(resources.ModelResource):
    class Meta:
        model = Interview

class OnboardingResource(resources.ModelResource):
    class Meta:
        model = Onboarding
        import_id_fields = ['doc_id']

# Additional resources for other models can be defined similarly

# Register models with ImportExportModelAdmin
@admin.register(candidateResume)
class CandidateResumeAdmin(ImportExportModelAdmin):
    resource_class = CandidateResumeResource
    list_display = ['candidate_id', 'name', 'phone_number', 'email', 'status']  # Removed 'id' if it doesn't exist

@admin.register(Interview)
class InterviewAdmin(ImportExportModelAdmin):
    resource_class = InterviewResource
    list_display = ['id', 'candidate_id', 'interviewMode', 'interviewRound', 'interviewDate', 'interviewTime', 'interviewround_remarks', 'interviewround_status']

@admin.register(Onboarding)
class OnboardingAdmin(ImportExportModelAdmin):
    resource_class = OnboardingResource
    list_display = ['doc_id', 'candidate_id_id', 'candidate_id']

@admin.register(HolidayMaster)
class HolidayMasterAdmin(ImportExportModelAdmin):
    list_display = ['year', 'name', 'remarks']

@admin.register(HolidayList)
class HolidayListAdmin(ImportExportModelAdmin):
    list_display = ['holiday_master', 'date', 'festival_name']

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    list_display = ['name', 'start_date', 'status']

@admin.register(CompanyBranch)
class CompanyBranchAdmin(ImportExportModelAdmin):
    list_display = ['company', 'name', 'status']

@admin.register(CompanyBankDetails)
class CompanyBankDetailsAdmin(ImportExportModelAdmin):
    list_display = ['company', 'bank_name', 'account_no', 'status']    

@admin.register(ShiftMaster)
class ShiftMasterAdmin(ImportExportModelAdmin):
    list_display = ['name', 'start_time', 'end_time']

@admin.register(Announcement)
class AnnouncementAdmin(ImportExportModelAdmin):
    list_display = ['name', 'created_on', 'message']

@admin.register(Policies)
class PoliciesAdmin(ImportExportModelAdmin):
    list_display = ['name', 'created_on', 'remarks']

@admin.register(WeekOff)
class WeekOffAdmin(ImportExportModelAdmin):
    list_display = ['name', 'remarks']

@admin.register(WeekOffNo)
class WeekOffNoAdmin(ImportExportModelAdmin):
    list_display = ['weekoff', 'week_no']

@admin.register(WeekOffDay)
class WeekOffDayAdmin(ImportExportModelAdmin):
    list_display = ['week_no', 'week_day', 'week_value']

@admin.register(CompanyPayrollDetails)
class CompanyPayrollDetailsAdmin(ImportExportModelAdmin):
    list_display = ['basic', 'hra', 'ca', 'sa', 'pt', 'employer_pf', 'employer_esic', 'employee_pf', 'employee_esic']
