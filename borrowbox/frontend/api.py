"""
DRF viewsets + custom workflow actions.

The custom actions enforce the BorrowBox workflow:

    Pending → Approved → Issued → Returned
    Pending → Rejected

Stock accounting invariant:
    approve  → no change
    reject   → no change
    issue    → decrement by request.quantity
    return   → increment by request.quantity, clamped at total_stock

Each transition is wrapped in transaction.atomic() with select_for_update()
on the Item row so two concurrent issues cannot oversell stock.
"""
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BorrowingRequest, Category, Employee, Item, Student
from .serializers import (
    BorrowingRequestSerializer,
    CategorySerializer,
    EmployeeSerializer,
    ItemSerializer,
    StudentSerializer,
)


# ---------------------------------------------------------------------------
# Plain CRUD viewsets
# ---------------------------------------------------------------------------
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer

    def get_queryset(self):
        qs = Item.objects.select_related('category').all()
        # ?available=true returns only items that have stock and are active
        if self.request.query_params.get('available') in ('true', '1', 'yes'):
            qs = qs.filter(is_active=True, available_stock__gt=0)
        return qs


# ---------------------------------------------------------------------------
# BorrowingRequest — CRUD plus workflow
# ---------------------------------------------------------------------------
class BorrowingRequestViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingRequestSerializer

    def get_queryset(self):
        return BorrowingRequest.objects.select_related('borrower', 'item').all()

    # ----- helpers -------------------------------------------------------
    def _set_actor(self, request, req, field: str):
        """Stamp the requesting user onto the audit field.

        When auth is open and the request is anonymous, fall back to an
        `actor` field in the body, or `system`.
        """
        if request.user and request.user.is_authenticated:
            actor = request.user.username
        else:
            actor = request.data.get('actor', '').strip() or 'system'
        setattr(req, field, actor)

    def _ensure_transition(self, req, allowed_from, to_state):
        if req.status not in allowed_from:
            raise ValueError(
                f"Illegal transition: {req.status} -> {to_state}. "
                f"Allowed source states: {sorted(allowed_from)}."
            )

    # ----- custom actions -----------------------------------------------
    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        """GET /api/requests/mine/?borrower=<student_id>"""
        borrower_id = request.query_params.get('borrower')
        if not borrower_id:
            return Response(
                {'detail': 'Query parameter `borrower` is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = self.get_queryset().filter(borrower_id=borrower_id)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        try:
            with transaction.atomic():
                self._ensure_transition(req, {'pending'}, 'approved')
                self._set_actor(request, req, 'approved_by_username')
                req.status = 'approved'
                req.approved_at = timezone.now()
                req.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        try:
            with transaction.atomic():
                self._ensure_transition(req, {'pending'}, 'rejected')
                self._set_actor(request, req, 'approved_by_username')
                req.status = 'rejected'
                req.approved_at = timezone.now()
                req.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        req = self.get_object()
        try:
            with transaction.atomic():
                self._ensure_transition(req, {'approved'}, 'issued')
                item = Item.objects.select_for_update().get(pk=req.item_id)
                if item.available_stock < req.quantity:
                    raise ValueError(
                        f"Cannot issue {req.quantity} of {item.name}: "
                        f"only {item.available_stock} in stock."
                    )
                item.available_stock -= req.quantity
                item.save()
                self._set_actor(request, req, 'issued_by_username')
                req.status = 'issued'
                req.issued_at = timezone.now()
                req.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['post'], url_path='return')
    def return_item(self, request, pk=None):
        """POST /api/requests/{id}/return/

        Method is named `return_item` (and given url_path='return') because
        DRF reserves `return` for the Response helper.  The URL pattern is
        `/return/`.
        """
        req = self.get_object()
        try:
            with transaction.atomic():
                self._ensure_transition(req, {'issued'}, 'returned')
                item = Item.objects.select_for_update().get(pk=req.item_id)
                # Clamp available_stock at total_stock in case totals were edited.
                item.available_stock = min(
                    item.total_stock,
                    item.available_stock + req.quantity,
                )
                item.save()
                self._set_actor(request, req, 'returned_by_username')
                req.status = 'returned'
                req.returned_at = timezone.now()
                req.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(req).data)