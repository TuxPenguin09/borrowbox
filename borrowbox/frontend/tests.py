"""
Sanity tests for BorrowBox backend.

These are smoke tests — they verify the wiring, not every business rule.
"""
from django.test import TestCase

from .models import BorrowingRequest, Category, Item, Student


class ApiRoutesExistTests(TestCase):
    def test_api_root_renders(self):
        resp = self.client.get('/api/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'students', resp.content)

    def test_lists_return_200(self):
        for url in ('/api/students/', '/api/employees/', '/api/categories/',
                    '/api/items/', '/api/requests/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class WorkflowTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='Electronics')
        self.item = Item.objects.create(
            name='Laptop', asset_tag='LAP-1', category=self.cat,
            total_stock=2, available_stock=2,
        )
        self.student = Student.objects.create(
            first_name='T', last_name='S', student_id_no='S-1',
            course='BSCS', year_level=1,
        )
        self.req = BorrowingRequest.objects.create(
            borrower=self.student, item=self.item, quantity=1,
        )

    def test_full_lifecycle_changes_stock_correctly(self):
        # approve -> stock unchanged
        self.client.post(f'/api/requests/{self.req.pk}/approve/',
                         {'actor': 't'}, format='json')
        self.item.refresh_from_db()
        self.assertEqual(self.item.available_stock, 2)

        # issue -> decrement
        self.client.post(f'/api/requests/{self.req.pk}/issue/',
                         {'actor': 't'}, format='json')
        self.item.refresh_from_db()
        self.assertEqual(self.item.available_stock, 1)

        # return -> increment
        self.client.post(f'/api/requests/{self.req.pk}/return/',
                         {'actor': 't'}, format='json')
        self.item.refresh_from_db()
        self.assertEqual(self.item.available_stock, 2)

    def test_reject_does_not_change_stock(self):
        self.client.post(f'/api/requests/{self.req.pk}/reject/',
                         {'actor': 't'}, format='json')
        self.item.refresh_from_db()
        self.assertEqual(self.item.available_stock, 2)

    def test_illegal_transition_is_blocked(self):
        resp = self.client.post(f'/api/requests/{self.req.pk}/issue/',
                                {'actor': 't'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_issue_fails_when_stock_insufficient(self):
        # Approve first to get into the right state.
        self.client.post(f'/api/requests/{self.req.pk}/approve/',
                         {'actor': 't'}, format='json')
        # Bump quantity above available stock and try to issue.
        self.req.refresh_from_db()
        self.req.quantity = 99
        self.req.save()
        resp = self.client.post(f'/api/requests/{self.req.pk}/issue/',
                                {'actor': 't'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.item.refresh_from_db()
        self.assertEqual(self.item.available_stock, 2)