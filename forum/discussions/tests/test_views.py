import json

from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from django.contrib.auth.models import User
from ..models import Category, Topic, Post, PostVotes
from feed.models import Subscription


class ForumViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_categories = 3

        for category_id in range(number_of_categories):
            Category.objects.create(category_name=f"Category {category_id}")

    def test_forum_view_url_exists_at_desired_location(self):
        response = self.client.get('/forums/')
        self.assertEqual(response.status_code, 200)

    def test_forum_view_url_accessible_by_name(self):
        response = self.client.get(reverse('discussions:forum'))
        self.assertEqual(response.status_code, 200)

    def test_forum_view_uses_correct_template(self):
        response = self.client.get(reverse('discussions:forum'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussions/forum.html')

    def test_forum_view_renders_five_categories(self):
        response = self.client.get(reverse('discussions:forum'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['categories_list']) == 3)


class CategoryViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        number_of_topics = 5

        for topic_id in range(number_of_topics):
            Topic.objects.create(topic_title=f"Topic {topic_id}", category=test_category, last_active_user=test_user)

    def test_category_view_url_exists_at_desired_location(self):
        response = self.client.get('/forums/1/')
        self.assertEqual(response.status_code, 200)

    def test_category_view_url_accessible_by_name(self):
        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)

    def test_category_view_uses_correct_template(self):
        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussions/category.html')

    def test_category_view_renders_five_topics(self):
        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['topics_list']), 5)


class TopicViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        test_topic = Topic.objects.create(topic_title="Topic", category=test_category, last_active_user=test_user)

        number_of_posts = 5

        for post_id in range(number_of_posts):
            Post.objects.create(topic=test_topic, post_body=f"Post {post_id}", author=test_user)

    def test_topic_view_url_exists_at_desired_location(self):
        response = self.client.get('/forums/topics/1/')
        self.assertEqual(response.status_code, 200)

    def test_topic_view_url_accessible_by_name(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)

    def test_topic_view_uses_correct_template(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussions/topic.html')

    def test_topic_view_renders_five_topics_for_unlogged_users(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_and_votes_list']), 5)

    def test_topic_view_renders_five_topics_for_logged_users(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_and_votes_list']), 5)

    def test_topic_view_renders_post_form(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('post_form' in response.context)

    def test_topic_view_renders_none_as_second_element_in_post_and_votes_list_for_unlogged_users(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        posts_and_votes_list = response.context['posts_and_votes_list']
        second_elements = [element[1] for element in posts_and_votes_list]
        for item in second_elements:
            self.assertIs(item, None)

    def test_topic_view_renders_zero_as_second_element_in_post_and_votes_list_for_logged_users(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        posts_and_votes_list = response.context['posts_and_votes_list']
        second_elements = [element[1] for element in posts_and_votes_list]
        for item in second_elements:
            self.assertEqual(item, 0)

    def test_topic_view_renders_false_issubscribed_for_unlogged_users(self):
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        is_subscribed = response.context['is_subscribed']
        self.assertFalse(is_subscribed)

    def test_topic_view_renders_false_issubscribed_for_logged_unsubscribed_users(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        is_subscribed = response.context['is_subscribed']
        self.assertFalse(is_subscribed)

    def test_topic_view_renders_true_issubscribed_for_logged_subscribed_users(self):
        test_user = User.objects.get(username='testuser')
        test_topic = Topic.objects.get(topic_title="Topic")
        Subscription.objects.create(user=test_user, topic=test_topic)
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        is_subscribed = response.context['is_subscribed']
        self.assertTrue(is_subscribed)

    def test_topic_view_renders_correct_post_votes(self):
        test_user = User.objects.get(username='testuser')
        test_topic = Topic.objects.get(topic_title="Topic")
        test_post = Post.objects.create(topic=test_topic, post_body="Post", author=test_user)

        PostVotes.objects.create(user=test_user, post=test_post, vote_value=1)

        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)

        posts_and_votes_list = response.context['posts_and_votes_list']
        second_elements = [element[1] for element in posts_and_votes_list]

        for i in range(len(second_elements)):
            if i == 0:
                self.assertEqual(second_elements[i], 1)
            else:
                self.assertEqual(second_elements[i], 0)

    def test_topic_view_successful_post_creation(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_and_votes_list']), 5)

        response = self.client.post(reverse('discussions:topic', kwargs={'topic_id': 1}),
                                    {'post_body': "Body of the new post"})
        self.assertRedirects(response, reverse('discussions:topic', kwargs={'topic_id': 1}))

        response = self.client.post(reverse('discussions:topic', kwargs={'topic_id': 1}),
                                    {'post_body': "Body of the second new post"}, follow=True)

        posts_and_votes_list = response.context['posts_and_votes_list']
        self.assertEqual(len(posts_and_votes_list), 7)

        last_post_body = posts_and_votes_list[0][0].post_body
        self.assertTrue(last_post_body == "Body of the second new post")

    def test_topic_view_unsuccessful_post_creation(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:topic', kwargs={'topic_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_and_votes_list']), 5)

        response = self.client.post(reverse('discussions:topic', kwargs={'topic_id': 1}),
                                    {'post_body': ""})
        self.assertEqual(response.status_code, 200)

        posts_and_votes_list = response.context['posts_and_votes_list']
        self.assertEqual(len(posts_and_votes_list), 5)

        last_post_body = posts_and_votes_list[0][0].post_body
        self.assertTrue(last_post_body == "Post 4")


class CreateTopicViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        test_topic = Topic.objects.create(topic_title="Topic", category=test_category, last_active_user=test_user)
        Post.objects.create(topic=test_topic, post_body="Post", author=test_user)

    def test_create_topic_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get('/forums/topics/new/')
        self.assertEqual(response.status_code, 200)

    def test_create_topic_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:new_topic'))
        self.assertEqual(response.status_code, 200)

    def test_create_topic_view_url_requires_registration(self):
        response = self.client.get(reverse('discussions:new_topic'))
        self.assertRedirects(response, '/login/?next=/forums/topics/new/')

    def test_create_topic_view_uses_correct_template(self):
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:new_topic'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussions/topic_create.html')

    def test_create_topic_view_successful_post_creation(self):
        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['topics_list']), 1)

        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('discussions:new_topic'), {'post_body': "Body of the new post",
                                                                       'topic_title': 'New Topic',
                                                                       'category': 1}, follow=True)

        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        topics_list = response.context['topics_list']
        self.assertEqual(len(topics_list), 2)
        self.assertTrue(topics_list[0].topic_title == "New Topic")

    def test_create_topic_view_unsuccessful_post_creation(self):
        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['topics_list']), 1)

        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('discussions:new_topic'), {'post_body': "",
                                                                       'topic_title': '',
                                                                       'category': 1}, follow=True)

        response = self.client.get(reverse('discussions:category', kwargs={'category_id': 1}))
        self.assertEqual(response.status_code, 200)
        topics_list = response.context['topics_list']
        self.assertEqual(len(topics_list), 1)
        self.assertTrue(topics_list[0].topic_title == "Topic")


class VotePostViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        test_category = Category.objects.create(category_name="Test Category")
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='1X<IMRUkw+tuK')
        test_user3 = User.objects.create_user(username='testuser3', password='1X<IKRUkw+tuK')
        test_topic = Topic.objects.create(topic_title="Topic", category=test_category, last_active_user=test_user1)
        test_post = Post.objects.create(topic=test_topic, post_body="Post 1", author=test_user1)

    def test_votepost_view_only_process_ajax_requests(self):
        login = self.client.login(username='testuser2', password='1X<IMRUkw+tuK')
        response = self.client.get('/post/vote/1/down/')
        self.assertEqual(response.status_code, 404)

    def test_votepost_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser2', password='1X<IMRUkw+tuK')
        response = self.client.get('/post/vote/1/up/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_votepost_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser2', password='1X<IMRUkw+tuK')
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_votepost_view_url_accessible_only_by_registered_users(self):
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

    def test_votepost_view_author_cannot_vote_for_own_posts(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'up'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_votepost_doubled_request(self):
        login = self.client.login(username='testuser2', password='1X<IMRUkw+tuK')
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'up'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        # requests with the same voting direction (up/up, down/down) from the same user should be ignored
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'up'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

        # but opposite directions should work
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        # also everything should work when the current voting state for this user is 0
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        # but voting total for this post and user cannot be -2 if it is already -1 or 2 if it is already 1
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_votepost_view_correct_total_votes_calculation(self):
        # one user upvotes - return votes==1 and prev_vote (for this user) == 0
        login = self.client.login(username='testuser2', password='1X<IMRUkw+tuK')
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'up'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'votes': 1, 'prev_vote': 0})

        # another user upvotes - return votes==2 and prev_vote (for this user) == 0
        login = self.client.login(username='testuser3', password='1X<IKRUkw+tuK')
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'up'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'votes': 2, 'prev_vote': 0})

        # the same user downvotes - return votes==1 and prev_vote (for this user) == 1
        response = self.client.get(reverse('discussions:vote_post', kwargs={'post_id': 1, 'direction': 'down'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'votes': 1, 'prev_vote': 1})


