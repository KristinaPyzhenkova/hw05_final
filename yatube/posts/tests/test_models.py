from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тest',
            slug='12345',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Number of values test',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        text = PostModelTest.post.text[:15]
        title = PostModelTest.group.title
        self.assertEqual(text, 'Number of value')
        self.assertEqual(title, self.group.title)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class FollowPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unfollower_user = User.objects.create_user(username='unfollower')
        cls.follower_user = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='following')
        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.author,
        )
        cls.post = Post.objects.create(
            text='Тест',
            author=cls.author,
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower_user)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollower_user)

    def test_follow_user_posts_in_line(self):
        """Новая запись пользователя появляется в ленте тех,
        кто подписан на этого пользователя."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        follower_post = len(response.context['page_obj'])
        self.assertEqual(follower_post, 1)

    def test_unfollow_user_no_posts_in_line(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто не подписан на этого пользователя."""
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        post = Post.objects.get(id=self.post.pk)
        self.assertNotIn(post, response.context['page_obj'])
