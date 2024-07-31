from django.contrib import admin
from .models import Employee, Department, Designation, Attendance, LeaveApplication,Work_Office,Position,Gender,ResignApplication, LeaveBalance

# Register your models here.
@admin.register(Department)
class CandidateDepartment(admin.ModelAdmin):
    pass

@admin.register(Designation)
class CandidateDesignation(admin.ModelAdmin):
    list_display = [id,"department","name"]
    

@admin.register(Employee)
class Employee(admin.ModelAdmin):
    list_display = [id,"emp_id","first_name", 'department', "status"]

@admin.register(Attendance)
class Attendance(admin.ModelAdmin):
    list_display = ['id', 'employee', 'date', 'clock_in','clock_out','is_full_day','is_half_day','is_absent']

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_from_date', 'leave_from_time', 'leave_to_date', 'leave_to_time', 'leave_type', 'leave_reason')


@admin.register(Work_Office)
class Work_Office(admin.ModelAdmin):
    pass

# @admin.register(Grade)
# class Grade(admin.ModelAdmin):
#     pass

@admin.register(Position)
class Position(admin.ModelAdmin):
    pass

@admin.register(Gender)
class Gender(admin.ModelAdmin):
    pass
@admin.register(ResignApplication)
class ResignApplication(admin.ModelAdmin):
    pass

@admin.register(LeaveBalance)
class LeaveBalance(admin.ModelAdmin):
    list_display = ('employee', 'total_leaves')