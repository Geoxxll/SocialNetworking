from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client
from django.contrib.auth.models import User
from socialNetworking.models.authors import Author
from socialNetworking.models.posts import Post

from socialNetworking.forms import PostForm
from datetime import datetime

class AddPostViewTest(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='TestUser', password='Test123')
        self.author = Author.objects.create(user=self.user)
        self.client.login(username='TestUser', password='Test123')
        
    def test_posts_list_GET(self):
        url = reverse('posts', kwargs={'author_id': self.author.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_posts_list_POST(self):
        url = reverse('posts', kwargs={'author_id': self.author.id})
        time = datetime.now()
        data = {
            'title': 'TestPost',
            'description': 'This is a test post.',
            'contentType': 'text/plain',
            'visibility': 'Public',
            'published_at': time,
            'author_of_posts': self.author.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(title='TestPost').exists())

    def test_posts_GET(self):
        post = Post.objects.create(title='TestPost', description='This is a test post.', author_of_posts=self.author)
        url = reverse('posts_id', kwargs={'author_id': self.author.id, 'post_id': post.post_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'TestPost')

    def test_posts_PUT(self):
        post = Post.objects.create(title='Test Post', description='This is a test post.', author_of_posts=self.author)
        url = reverse('posts_id', kwargs={'author_id': self.author.id, 'post_id': post.post_id})
        data = {
            'title': 'UpdatedPost',
            'description': 'This is an updated test post.'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'UpdatedPost')

    def test_posts_DELETE(self):
        post = Post.objects.create(title='TestPost', description='This is a test post.', author_of_posts=self.author)
        url = reverse('posts_id', kwargs={'author_id': self.author.id, 'post_id': post.post_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(title='TestPost').exists())


# class UserAuthorTestCase(APITestCase):

#     def setUp(self):
#         pass

#     def test_author_creation(self):
#         pass

#     def test_author_editing(self):
#         pass

#     def test_author_list(self):
#         pass

# class PostingTestCase(APITestCase):
#     pass

# class CommentingTestCase(APITestCase):
#     pass