import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from django.conf import settings
from posts.models import Group, Post, Comment
from posts.forms import PostForm, CommentForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='hello')
        cls.group = Group.objects.create(
            title='Тest group',
            slug='test-slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test',
            pub_date='22.02.2022',
            pk=100,
        )
        cls.form = PostForm()
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_for_guest_client(self):
        """Тест для неавторизованного пользователя на создание поста."""
        posts_count_create = Post.objects.count()
        form_data_create = {
            'text': 'Test1',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count_create)

    def test_create_post_for_authorized_client(self):
        """Тест для авторизованного пользователя на создание поста."""
        posts_count_create = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data_create = {
            'text': 'Test2',
            'group': self.group.pk,
            'pk': 101,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'hello'})
        )
        self.assertEqual(Post.objects.count(), posts_count_create + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test2',
                pk=101,
                author=self.user,
                group=self.group,
                image=self.post.image
            ).exists()
        )

    def test_post_edit(self):
        """Тест для автор. пользователя на редактирование поста."""
        posts_count_edit = Post.objects.count()
        form_data_edit = {
            'text': 'Test update',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            (reverse('posts:post_edit', kwargs={'post_id': 100})),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 100})
        )
        self.assertEqual(Post.objects.count(), posts_count_edit)
        self.assertTrue(
            Post.objects.filter(
                pk=100,
                text='Test update',
            ).exists()
        )

    def test_comment_creat(self):
        """Тест для создания комментария автор. пользователя и нет."""
        comment_count = Comment.objects.count()
        form_data_comment = {
            'text': 'Test comment',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 100}),
            data=form_data_comment,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 100})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
