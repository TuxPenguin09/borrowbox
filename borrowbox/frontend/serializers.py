from rest_framework import serializers

from .models import Employee, Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'first_name', 'last_name', 'student_id_no',
            'email', 'course', 'year_level',
            'is_active', 'created_at',
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name', 'last_name', 'employee_id_no',
            'email', 'department', 'position',
            'is_active', 'created_at',
        ]
