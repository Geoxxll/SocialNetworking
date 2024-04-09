from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client
from django.contrib.auth.models import User
from socialNetworking.models.authors import Author
from socialNetworking.models.posts import Post
from socialNetworking.models.followers import Follower

from socialNetworking.forms import PostForm
import json
from django.utils import timezone
import os
import base64
import uuid

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
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, "testImage", "image.png")
        self.image = open(image_path, "rb").read()
        content = base64.b64encode(self.image)
        self.image_post = Post.objects.create(
            title='ImageTestPost', 
            description='This is an image post', 
            contentType='image/png;base64', 
            author_of_posts=self.author,
            content=content,    
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
        followerUser = User.objects.create_user(username='TestUser_Follower', password='Test123')
        follower = Author.objects.create(
            user=followerUser,
            url='https://test.com/authors/2',
            host='https://test.com',
            displayName='TestUser_Follower',
            github='https://github.com/test_user_follower',
            profileImagePicture=None,
            draftProfileImage=None,
            draftDisplayName='',
            draftGithub='',
            lastCommitFetch=None,
            is_approved=True  # Adjust as needed
        )
        time = timezone.now()
        follower_object = Follower.objects.create(
            follower=follower,
            followee=self.author,
            followed_at=time
        )
        url = reverse('followers', kwargs={'author_id':self.author.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'][0]['displayName'], 'TestUser_Follower')

    def test_image_GET(self):
        request_url = reverse('image', kwargs={'author_id': self.author.id, 'post_id': self.image_post.post_id})
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, self.image)
    def test_image_GET_author_not_found(self):
        flaged_author_id = uuid.uuid4()
        request_url = reverse('image', kwargs={'author_id': flaged_author_id, 'post_id': self.image_post.post_id})
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_image_GET_post_not_found(self):
        flaged_post_id = uuid.uuid4()
        request_url = reverse('image', kwargs={'author_id': self.author.id, 'post_id': flaged_post_id})
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_image_GET_invalid_content_type(self):
        self.image_post.contentType = 'text/plain'
        self.image_post.save()
        request_url = reverse('image', kwargs={'author_id':self.author.id, 'post_id': self.image_post.post_id})
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comments_GET(self):
        pass

    def test_comments_POST(self):
        pass
