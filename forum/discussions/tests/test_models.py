import mock
import datetime

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Category, Topic, Post, PostVotes


class CategoryModelTests(TestCase):

    def setUp(self):
        Category.objects.create(category_name="Test Category")

    def test_zero_topics_amount_after_category_creation(self):
        """
        topics_amount field should be equal to 0 after new category creation
        """
        category = Category.objects.get(category_name="Test Category")
        self.assertEqual(category.topics_amount, 0)

    def test_date_after_category_creation(self):
        """
        last_updated_date field should be equal to the time at the moment of creation after creation
        """
        testtime = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            category = Category.objects.create(category_name="New Test Category")

        self.assertEqual(category.last_updated_date, testtime)

    def test_date_after_category_updating(self):
        """
        last_updated_date field should be equal to the time at the moment of updating after updating
        """
        testtime = timezone.now()
        category = Category.objects.get(category_name="Test Category")
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            category.topics_amount += 1
            category.save()
        self.assertEqual(category.last_updated_date, testtime)


class TopicModelTests(TestCase):

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_topic = Topic.objects.create(category=test_category, topic_title='Test Topic', last_active_user=test_user1)

    def test_creation_date_equals_last_updated_date_after_topic_creation(self):
        test_topic = Topic.objects.get(topic_title='Test Topic')
        self.assertTrue(abs(test_topic.last_updated_date - test_topic.creation_date) < datetime.timedelta(seconds=0.5))

    def test_correctness_of_posts_amount_calculation(self):
        test_topic = Topic.objects.get(topic_title='Test Topic')
        test_user1 = User.objects.get(username='testuser1')
        for i in range(3):
            Post.objects.create(topic=test_topic, post_body=f"Body of post #{i}", author=test_user1)
        self.assertEqual(test_topic.posts_amount, 3)
        self.assertFalse(test_topic.posts_amount == 0)

    def test_last_active_user_updating_after_posts_creation(self):
        test_topic = Topic.objects.get(topic_title='Test Topic')
        test_user2 = User.objects.get(username='testuser2')
        self.assertFalse(test_topic.last_active_user == test_user2)

        Post.objects.create(topic=test_topic, post_body=f"Body of post", author=test_user2)
        self.assertTrue(test_topic.last_active_user == test_user2)

    def test_date_after_topic_creation(self):
        testtime = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            test_category = Category.objects.get(category_name="Test Category")
            test_user = User.objects.get(username='testuser1')
            topic = Topic.objects.create(category=test_category, topic_title='Topic0', last_active_user=test_user)

        self.assertEqual(topic.last_updated_date, testtime)

    def test_date_after_topic_updating(self):
        testtime = timezone.now()
        test_topic = Topic.objects.get(topic_title='Test Topic')
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            test_topic.posts_amount += 1
            test_topic.save()
        self.assertEqual(test_topic.last_updated_date, testtime)


class PostModelTests(TestCase):

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user3 = User.objects.create_user(username='testuser3', password='2HJ1vTV0Z&3iD')
        test_topic = Topic.objects.create(category=test_category, topic_title='Test Topic', last_active_user=test_user1)
        Post.objects.create(topic=test_topic, post_body=f"Body of post", author=test_user1)

    def test_correctness_of_votes_calculation(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        test_post = Post.objects.get(post_body=f"Body of post", author=test_user1)
        # test initial state
        self.assertEqual(test_post.votes(), 0)

        # test upvoting
        vote1 = PostVotes.objects.create(user=test_user2, post=test_post, vote_value=1)
        vote2 = PostVotes.objects.create(user=test_user3, post=test_post, vote_value=1)
        self.assertEqual(test_post.votes(), 2)

        vote1.delete()
        vote2.delete()

        # test downvoting
        vote1 = PostVotes.objects.create(user=test_user2, post=test_post, vote_value=-1)
        vote2 = PostVotes.objects.create(user=test_user3, post=test_post, vote_value=-1)
        self.assertEqual(test_post.votes(), -2)

        vote1.delete()
        vote2.delete()

        # test both directions
        vote1 = PostVotes.objects.create(user=test_user2, post=test_post, vote_value=-1)
        vote2 = PostVotes.objects.create(user=test_user3, post=test_post, vote_value=1)
        self.assertEqual(test_post.votes(), 0)
