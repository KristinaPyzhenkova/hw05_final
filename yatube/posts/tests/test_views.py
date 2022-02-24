import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Post, Group, Follow, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='22.02.2022',
            pk=100,
            image=SimpleUploadedFile(
                name='small.gif',
                content=(
                    b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B'
                ),
                content_type='image/gif',
            )
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_view_create_correct(self):
        """Создание нового поста и переодрессация на профайла Автора. """
        form_data_create = {
            'text': 'Test #2',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'HasNoName'})
        )

    def test_view_create_correct_on_group_list(self):
        """Корректное отображение созданного поста на странице группы. """
        form_data_create = {
            'text': 'Test #2',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        response = self.authorized_client.post(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        text = first_object.text
        group = first_object.group
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(text, 'Test #2')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_view_create_correct_on_main(self):
        """Корректное отображение созданного поста на главной странице."""
        form_data_create = {
            'text': 'Test #2',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        response = self.authorized_client.post(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        text = first_object.text
        group = first_object.group
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(text, 'Test #2')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_view_correct_group_post(self):
        """Отуствие созданного поста в других группах. """
        Group.objects.create(
            title='Тестовая группа2',
            description='Тестовое описание2',
            slug='test2-slug')
        form_data_create = {
            'text': 'Test #2',
            'group': 2
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        response = self.authorized_client.post(reverse(
            'posts:group_list', kwargs={'slug': 'test2-slug'}
        ))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        self.assertFalse(text == 'Тестовый текст')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            )): 'posts/group_list.html',
            (reverse(
                'posts:profile', kwargs={'username': 'HasNoName'}
            )): 'posts/profile.html',
            (reverse(
                'posts:post_detail', kwargs={'post_id': 100}
            )): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create.html',
            (reverse(
                'posts:post_edit', kwargs={'post_id': 100}
            )): 'posts/create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 100}
        ))
        first_object = response.context['post']
        post_id = first_object.pk
        author = first_object.author
        text = first_object.text
        group = first_object.group
        image = first_object.image
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(post_id, 100)
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertEqual(image.name, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'HasNoName'}
        ))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        text = first_object.text
        group = first_object.group
        image = first_object.image
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertEqual(image.name, 'posts/small.gif')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        text = first_object.text
        group = first_object.group
        image = first_object.image
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertEqual(image.name, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        text = first_object.text
        group = first_object.group
        self.assertEqual(author.username, 'HasNoName')
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context.get('is_edit')
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertFalse(is_edit)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 100}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context.get('is_edit')
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertTrue(is_edit)

    def test_cache_index_page(self):
        """Корректность работы кеша на главной стр."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_check = response.content
        post = Post.objects.get(pk=100)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.number_of_posts = 13
        Post.objects.bulk_create([
            Post(
                author=cls.author,
                group=cls.group,
                text=f'Test {post}',
                pub_date='22.02.2022'
            )
            for post in range(cls.number_of_posts)
        ])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_paginator(self):
        """Тест корректности паджинатора."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'page_obj',
            (reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            )): 'page_obj',
            (reverse(
                'posts:profile', kwargs={'username': 'HasNoName'}
            )): 'page_obj',
        }
        self.authorized_client.force_login(self.author)
        for reverse_name, page_obj in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.authorized_client.force_login(self.author)
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[page_obj]), 10)


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
        """Создаем подписку на автора."""
        self.unfollower_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author,
        ).exists())

    def test_unfollow_user_no_posts_in_line(self):
        """Удаляем подписку на автора."""
        Follow.objects.create(user=self.follower_user, author=self.author)
        self.assertTrue(Follow.objects.filter(
            user=self.follower_user, author=self.author
        ).exists())
        self.follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertFalse(Follow.objects.filter(
            user=self.follower_user, author=self.author
        ))

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


class CommentPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user')
        cls.author_2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='22.02.2022',
            pk=100,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Комментарий №1',
            post=cls.post
        )

    def setUp(self):
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.author)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.author_2)

    def test_comment_post_from_authorized_client(self):
        """Авторизованный пользователь может комментировать посты."""
        comment_count = Comment.objects.count()
        form_data_create = {
            'text': 'Комментарий №2',
            'post': self.post,
            'author': self.author_2
        }
        self.authorized_client_2.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data_create,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
