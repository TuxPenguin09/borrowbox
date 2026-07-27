"""
BorrowBox domain models.

Six entities (plus Django's auth.User, augmented with a `role` field via
UserProfile).  The borrower on a BorrowingRequest is always a Student in this
MVP — supporting Employee-as-borrower would require GenericForeignKey /
contenttypes, which is too much for a school demo.
"""
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------------------------------------------------------
# User role (admin / custodian).  Open auth for the MVP; this just labels
# people so the admin UI and future permission checks can distinguish them.
# ---------------------------------------------------------------------------
class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    CUSTODIAN = 'custodian', 'Custodian'


class UserProfile(models.Model):
    """Role + metadata for an auth.User.  Created via signal on first save."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTODIAN,
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------
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


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', 'New'
        GOOD = 'good', 'Good'
        FAIR = 'fair', 'Fair'
        POOR = 'poor', 'Poor'

    name = models.CharField(max_length=120)
    asset_tag = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,        # cannot delete a category that owns items
        related_name='items',
    )
    description = models.TextField(blank=True)
    condition = models.CharField(
        max_length=10,
        choices=Condition.choices,
        default=Condition.GOOD,
    )
    total_stock = models.PositiveIntegerField(default=1)
    available_stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.asset_tag} – {self.name}"

    @property
    def is_available(self) -> bool:
        return self.is_active and self.available_stock > 0


class BorrowingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        ISSUED = 'issued', 'Issued'
        RETURNED = 'returned', 'Returned'
        REJECTED = 'rejected', 'Rejected'

    borrower = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='borrowing_requests',
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='borrowing_requests',
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Approval/issuance audit fields stored as username strings so seed data
    # can run without every actor having a real Django User.
    approved_by_username = models.CharField(max_length=150, blank=True)
    issued_by_username = models.CharField(max_length=150, blank=True)
    returned_by_username = models.CharField(max_length=150, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"#{self.pk} {self.borrower_id} → {self.item_id} ({self.status})"


# ---------------------------------------------------------------------------
# Auto-create a UserProfile whenever an auth.User is saved.
# ---------------------------------------------------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def _ensure_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)