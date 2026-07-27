from django.contrib import admin

from .models import (
    BorrowingRequest,
    Category,
    Employee,
    Item,
    Student,
    UserProfile,
)


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'name', 'category', 'total_stock', 'available_stock', 'condition', 'is_active')
    search_fields = ('asset_tag', 'name')
    list_filter = ('category', 'condition', 'is_active')
    autocomplete_fields = ('category',)


@admin.register(BorrowingRequest)
class BorrowingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'borrower', 'item', 'quantity', 'status', 'requested_at')
    list_filter = ('status',)
    search_fields = ('borrower__student_id_no', 'item__asset_tag')
    readonly_fields = ('requested_at', 'approved_at', 'issued_at', 'returned_at',
                       'approved_by_username', 'issued_by_username', 'returned_by_username')


admin.site.register(UserProfile)