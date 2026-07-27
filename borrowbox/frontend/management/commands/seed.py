"""
Seed demo data for BorrowBox.

Idempotent: safe to run more than once.  Re-running will not duplicate rows;
it also will not wipe rows the user created by hand.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from frontend.models import (
    BorrowingRequest,
    Category,
    Employee,
    Item,
    Student,
)


SEED_CATEGORIES = [
    ('Electronics', 'Laptops, projectors, cables'),
    ('Books', 'Textbooks and reference materials'),
]

SEED_ITEMS = [
    # (name, asset_tag, category_index, total, available, condition)
    ('Dell Latitude 7420',     'ELEC-0001', 0, 5, 5, 'good'),
    ('Logitech MX Master 3',   'ELEC-0002', 0, 8, 8, 'new'),
    ('Epson Projector EB-X41', 'ELEC-0003', 0, 3, 3, 'good'),
    ('Calculus Textbook 12e',  'BOOK-0001', 1, 10, 10, 'good'),
    ('Physics Workbook 4e',    'BOOK-0002', 1, 12, 12, 'fair'),
]

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
    help = "Seed BorrowBox with demo users, categories, items, students, employees."

    def handle(self, *args, **options):
        # ----- superuser --------------------------------------------------
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

        # ----- categories -------------------------------------------------
        cat_objs = []
        for name, desc in SEED_CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={'description': desc})
            cat_objs.append(cat)

        # ----- items ------------------------------------------------------
        item_objs = []
        for name, tag, cat_idx, total, available, condition in SEED_ITEMS:
            item, _ = Item.objects.get_or_create(
                asset_tag=tag,
                defaults={
                    'name': name,
                    'category': cat_objs[cat_idx],
                    'total_stock': total,
                    'available_stock': available,
                    'condition': condition,
                },
            )
            item_objs.append(item)

        # ----- students ---------------------------------------------------
        student_objs = []
        for first, last, sid, email, course, yr in SEED_STUDENTS:
            s, _ = Student.objects.get_or_create(
                student_id_no=sid,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': email, 'course': course, 'year_level': yr,
                },
            )
            student_objs.append(s)

        # ----- employees --------------------------------------------------
        for first, last, eid, email, dept, pos in SEED_EMPLOYEES:
            Employee.objects.get_or_create(
                employee_id_no=eid,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': email, 'department': dept, 'position': pos,
                },
            )

        # ----- one sample Pending request ---------------------------------
        if not BorrowingRequest.objects.filter(status='pending').exists():
            BorrowingRequest.objects.create(
                borrower=student_objs[0],
                item=item_objs[0],
                quantity=1,
                notes='Projector for thesis defense rehearsal.',
            )
            self.stdout.write(self.style.SUCCESS(
                "Created 1 sample Pending BorrowingRequest."))

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Users={User.objects.count()} "
            f"Categories={Category.objects.count()} "
            f"Items={Item.objects.count()} "
            f"Students={Student.objects.count()} "
            f"Employees={Employee.objects.count()} "
            f"Requests={BorrowingRequest.objects.count()}"
        ))