import mock

from django.utils import timezone
from django.test import TestCase

from .models import Category


class CategoryModelTests(TestCase):

    def setUp(self):
        Category.objects.create(category_name="Test Category")

    def test_zero_topics_amount_after_creation(self):
        """
        topics_amount field should be equal to 0 after new category creation
        """
        category = Category.objects.get(category_name="Test Category")
        self.assertIs(category.topics_amount, 0)

    def test_date_after_creation(self):
        """
        last_updated_date field should be equal to the time at the moment of creation after creation
        """
        testtime = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            category = Category.objects.create(category_name="New Test Category")

        self.assertIs(category.last_updated_date, testtime)

    def test_date_after_updating(self):
        """
        last_updated_date field should be equal to the time at the moment of updating after updating
        """
        testtime = timezone.now()
        category = Category.objects.get(category_name="Test Category")
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            category.topics_amount += 1
            category.save()
        self.assertIs(category.last_updated_date, testtime)
