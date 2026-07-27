from django.contrib import admin

from .models import Employee, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id_no', 'last_name', 'first_name', 'course', 'year_level', 'is_active')
    search_fields = ('student_id_no', 'first_name', 'last_name', 'email')
    list_filter = ('course', 'year_level', 'is_active')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id_no', 'last_name', 'first_name', 'department', 'position', 'is_active')
    search_fields = ('employee_id_no', 'first_name', 'last_name', 'email')
    list_filter = ('department', 'is_active')
