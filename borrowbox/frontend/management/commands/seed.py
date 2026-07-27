from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from frontend.models import Employee, Student


SEED_STUDENTS = [
    # (first, last, student_id_no, email, course, year_level)
    ('Juan',   'Dela Cruz', 'STU-2026-0001', 'juan@example.edu',   'BSCS', 2),
    ('Maria',  'Santos',    'STU-2026-0002', 'maria@example.edu',  'BSIT', 3),
    ('Andres', 'Bonifacio', 'STU-2026-0003', 'andres@example.edu', 'BSCE', 1),
]

SEED_EMPLOYEES = [
    # (first, last, employee_id_no, email, department, position)
    ('Carla', 'Reyes',  'EMP-2026-0001', 'carla@example.edu', 'Library',   'Head Librarian'),
    ('Diego', 'Lazaro', 'EMP-2026-0002', 'diego@example.edu', 'IT Office', 'IT Officer'),
]


class Command(BaseCommand):
    help = "Seed BorrowBox with demo users, students, and employees."

    def handle(self, *args, **options):
        # superuser
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.edu',
            },
        )
        if created:
            admin.set_password('admin12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                "Created superuser 'admin' / 'admin12345'."))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # students
        for first, last, sid, email, course, yr in SEED_STUDENTS:
            Student.objects.get_or_create(
                student_id_no=sid,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': email, 'course': course, 'year_level': yr,
                },
            )

        # employees
        for first, last, eid, email, dept, pos in SEED_EMPLOYEES:
            Employee.objects.get_or_create(
                employee_id_no=eid,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': email, 'department': dept, 'position': pos,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Users={User.objects.count()} "
            f"Students={Student.objects.count()} "
            f"Employees={Employee.objects.count()}"
        ))
