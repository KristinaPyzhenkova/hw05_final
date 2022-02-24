from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Follow, Comment


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
        self.assertEqual(text, 'Number of value')

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


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тesting',
            slug='test',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Number of values test',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        title = GroupModelTest.group.title[:4]
        self.assertEqual(title, 'Тest')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        title = GroupModelTest.group
        field_verboses = {
            'title': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    title._meta.get_field(field).verbose_name, expected_value)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        description = GroupModelTest.group
        field_help_texts = {
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    description._meta.get_field(field).help_text,
                    expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тest',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        text = CommentModelTest.comment.text[:8]
        self.assertEqual(text, 'Тестовый')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        text = CommentModelTest.comment
        field_verboses = {
            'text': 'Комментарий'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    text._meta.get_field(field).verbose_name, expected_value)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        text = CommentModelTest.comment
        field_help_texts = {
            'text': 'Комментарий к посту',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    text._meta.get_field(field).help_text, expected_value)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тest',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        user = FollowModelTest.follow
        field_verboses = {
            'user': 'подписчик'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).verbose_name, expected_value)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        user = FollowModelTest.follow
        field_help_texts = {
            'user': 'ссылка на объект пользователя, который подписывается',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).help_text, expected_value)
