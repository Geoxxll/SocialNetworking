from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client
from django.contrib.auth.models import User
from socialNetworking.models.authors import Author
from socialNetworking.models.posts import Post

from socialNetworking.forms import PostForm
import json
from django.utils import timezone

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

    def test_posts_GET(self):
        post = Post.objects.create(title='TestPost', description='This is a test post.', author_of_posts=self.author)
        url = reverse('posts_id', kwargs={'author_id': self.author.id, 'post_id': post.post_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'TestPost')

    def test_posts_DELETE(self):
        post = Post.objects.create(title='TestPost', description='This is a test post.', author_of_posts=self.author)
        url = reverse('posts_id', kwargs={'author_id': self.author.id, 'post_id': post.post_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(title='TestPost').exists())

class AddAuthorTest(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='TestUser', password='Test123')
        self.client.login(username='TestUser', password='Test123')
        self.author = Author.objects.create(
            user=self.user,
            url='https://test.com/authors/1',
            host='https://test.com',
            displayName='TestUser',
            github='https://github.com/test_user',
            profileImagePicture=None,
            draftProfileImage=None,
            draftDisplayName='',
            draftGithub='',
            lastCommitFetch=None,
            is_approved=True  # Adjust as needed
        )
    def test_author_GET(self):
        url = reverse('authors_id', kwargs={'author_id': self.author.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_PUT(self):
        url = reverse('authors_id', kwargs={'author_id': self.author.id})
        data = {
            "displayName": 'UpdatedUser',
            "url": self.author.url,
            "host": self.author.host
        }
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['displayName'], 'UpdatedUser')
    
    def test_authors_GET(self):
        url = reverse('authors')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_followers_GET(self):
        pass
