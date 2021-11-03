from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_not_author = User.objects.create_user(
            username='test_user_not_author'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост тестового пользователя в тестовой группе',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client_not_author = Client()

        self.auth_client.force_login(PostsURLTests.user)
        self.auth_client_not_author.force_login(PostsURLTests.user_not_author)

    def test_urls_exists_at_desired_location(self):
        """Проверяем доступность страниц приложения Posts."""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_names = [
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post.pk}/',
            f'/posts/{post.pk}/edit/',
            '/create/',
            '/fake_page/',
        ]

        for adress in url_names:
            with self.subTest(adress=adress):
                guest_response = self.guest_client.get(adress, follow=True)
                auth_response = self.auth_client.get(adress)

                if adress == f'/posts/{post.pk}/edit/':
                    self.assertRedirects(
                        guest_response,
                        f'/auth/login/?next=/posts/{post.pk}/edit/'
                    )

                    self.assertEqual(
                        auth_response.reason_phrase, 'OK'
                    )

                    auth_not_author_response = (
                        self.auth_client_not_author.get(adress)
                    )
                    self.assertEqual(
                        auth_not_author_response.url,
                        f'/posts/{post.pk}'
                    )
                    continue

                if adress == '/create/':
                    self.assertRedirects(
                        guest_response,
                        f'{"/auth/login/?next=/create/"}'
                    )
                    self.assertEqual(auth_response.reason_phrase, 'OK')
                    continue

                if adress == '/fake_page/':
                    self.assertEqual(guest_response.reason_phrase, 'Not Found')
                    self.assertEqual(auth_response.reason_phrase, 'Not Found')
                    continue

                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны приложения Posts."""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for adress, template in url_templates_names.items():
            with self.subTest(adress=adress):
                response = self.auth_client.get(adress)
                self.assertTemplateUsed(response, template)
