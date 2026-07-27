"""
DRF serializers for BorrowBox.

One ModelSerializer per entity, kept in a single file because the project is
small.  The interesting detail is that BorrowingRequestSerializer marks
`status` and the four audit fields as read-only — clients can only advance
the state machine through the custom @action endpoints on the viewset.
"""
from rest_framework import serializers

from .models import (
    BorrowingRequest,
    Category,
    Employee,
    Item,
    Student,
    UserProfile,
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role']


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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class ItemSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'name', 'asset_tag',
            'category', 'category_id',
            'description', 'condition',
            'total_stock', 'available_stock',
            'is_active', 'created_at',
            'is_available',
        ]


class BorrowingRequestSerializer(serializers.ModelSerializer):
    borrower_name = serializers.CharField(source='borrower.__str__', read_only=True)
    item_name = serializers.CharField(source='item.__str__', read_only=True)

    class Meta:
        model = BorrowingRequest
        fields = [
            'id',
            'borrower', 'borrower_name',
            'item', 'item_name',
            'quantity', 'status',
            'approved_by_username', 'issued_by_username', 'returned_by_username',
            'requested_at', 'approved_at', 'issued_at', 'returned_at',
            'notes',
        ]
        read_only_fields = [
            'status',
            'approved_by_username', 'issued_by_username', 'returned_by_username',
            'requested_at', 'approved_at', 'issued_at', 'returned_at',
        ]