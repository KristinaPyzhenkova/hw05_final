from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.user = User.objects.create_user(username='HasNoName2')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='22.02.2022',
            pk=100
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_url_status_code(self):
        """Праивльный статус код на стронице."""
        url_status_code = {
            reverse('posts:index'): 200,
            reverse('about:tech'): 200,
            reverse('about:author'): 200,
            reverse('posts:post_create'): 302,
            '/unexisting_page/': 404,
        }
        for address, status_code in url_status_code.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
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
            (reverse(
                'posts:post_edit', kwargs={'post_id': 100}
            )): 'posts/create.html',
            reverse('posts:post_create'): 'posts/create.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.authorized_client.force_login(self.author)
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_edit_redirect_guest(self):
        """Страница по адресу /posts/../edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get((reverse(
            'posts:post_edit', kwargs={'post_id': 100}
        )), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/100/edit/'
        )

    def test_urls_edit_redirect_user2(self):
        """Страница по адресу /posts/../edit/ перенаправит зарег.
        пользователя(не автора) на страницу поста.
        """
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get((reverse(
            'posts:post_edit', kwargs={'post_id': 100}
        )), follow=True)
        self.assertRedirects(
            response, (reverse(
                'posts:post_detail', kwargs={'post_id': 100}
            ))
        )
