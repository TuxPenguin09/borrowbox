from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    student_id_no = models.CharField(max_length=40, unique=True)
    email = models.EmailField(blank=True)
    course = models.CharField(max_length=120, blank=True)
    year_level = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.student_id_no} – {self.last_name}, {self.first_name}"


class Employee(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    employee_id_no = models.CharField(max_length=40, unique=True)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=120, blank=True)
    position = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.employee_id_no} – {self.last_name}, {self.first_name}"
