from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Employee, Department, Designation, Attendance, LeaveApplication, Work_Office, Position, Gender, ResignApplication, LeaveBalance

# Define Resource classes for all models
class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department

class DesignationResource(resources.ModelResource):
    class Meta:
        model = Designation

class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        import_id_fields = ['emp_id']

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance

class LeaveApplicationResource(resources.ModelResource):
    class Meta:
        model = LeaveApplication

class WorkOfficeResource(resources.ModelResource):
    class Meta:
        model = Work_Office
        import_id_fields = ['office_id'] 

class PositionResource(resources.ModelResource):
    class Meta:
        model = Position

class GenderResource(resources.ModelResource):
    class Meta:
        model = Gender

class ResignApplicationResource(resources.ModelResource):
    class Meta:
        model = ResignApplication

class LeaveBalanceResource(resources.ModelResource):
    class Meta:
        model = LeaveBalance

# Register your models with ImportExportModelAdmin

@admin.register(Department)
class CandidateDepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource

@admin.register(Designation)
class CandidateDesignationAdmin(ImportExportModelAdmin):
    resource_class = DesignationResource
    list_display = ['department', 'name']  # pk used instead of id

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = [ 'emp_id', 'first_name', 'department', 'status']  # pk used instead of id

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResource
    list_display = ['employee', 'date', 'clock_in', 'clock_out', 'is_full_day', 'is_half_day', 'is_absent']  # pk used instead of id

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(ImportExportModelAdmin):
    resource_class = LeaveApplicationResource
    list_display = ['employee', 'leave_from_date', 'leave_from_time', 'leave_to_date', 'leave_to_time', 'leave_type', 'leave_reason']

@admin.register(Work_Office)
class WorkOfficeAdmin(ImportExportModelAdmin):
    resource_class = WorkOfficeResource

@admin.register(Position)
class PositionAdmin(ImportExportModelAdmin):
    resource_class = PositionResource

@admin.register(Gender)
class GenderAdmin(ImportExportModelAdmin):
    resource_class = GenderResource

@admin.register(ResignApplication)
class ResignApplicationAdmin(ImportExportModelAdmin):
    resource_class = ResignApplicationResource

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(ImportExportModelAdmin):
    resource_class = LeaveBalanceResource
    list_display = ['employee', 'total_leaves']
