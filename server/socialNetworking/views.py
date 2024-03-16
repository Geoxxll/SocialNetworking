from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.utils import timezone
from django.views import View
from .models.posts import Post
from .models.comments import Comment
from .models.followers import Follower
from .models.follow import Follow
from .models.likes import Like
from .models.inbox import Inbox
from .models.inbox_item import InboxItem
from .forms import PostForm, CommentForm, ShareForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from .models.authors import Author
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.core.paginator import Paginator

from django.http import JsonResponse
from .serializers import (
  AuthorSerializer, 
  FollowerSerializer,
  FollowSerializer, 
  TextPostSerializer, 
  CommentSerializer,
  LikeSerializer
  )
from rest_framework.response import Response
from rest_framework import status

import requests
from datetime import datetime, timedelta
from django.utils import timezone

class AddPostView(View):
    def get(self, request, *args, **kwargs):
        # posts = Post.objects.all().order_by('-published_at')
        form = PostForm()
        follow_requests = Follow.objects.filter(object_of_follow__user = request.user, active = True)

        context = {
            
            'form': form,
            'follow_requests': follow_requests,
        }

        # return render(request, 'socialNetworking/post_list.html', context)
        return render(request, 'socialNetworking/post_list.html', context)
    
    def post(self, request, *args, **kwargs):
        
        form = PostForm(request.POST)
        share_form = ShareForm()

        if form.is_valid():
             # Retrieve the User instance associated with the request
            user_instance = request.user if isinstance(request.user, User) else User.objects.get(username=request.user)

            # Retrieve or create Author instance associated with the User
            author_instance = Author.objects.get(user=user_instance)
            new_post = form.save(commit=False)
            new_post.author_of_posts = author_instance
            new_post.url = author_instance.url + "/posts/" + str(new_post.post_id)
            new_post.save()
            
            # Create a new, empty form after successfully saving the post
            form = PostForm()
            
        posts = Post.objects.all().order_by('-published_at')
        context = {
            'post_list': posts,
            'form': form,
            'shareform': share_form,
        }

        return render(request, 'socialNetworking/dashboard.html', context)

class FindFriendsView(View):
    def get(self, request, *args, **kwargs):
        User = get_user_model()
        query = request.GET.get('query')
        
        if query:
            # Filter users based on the search query
            all_users = Author.objects.filter(displayName__icontains=query).order_by('-displayName')
        else:
            # Retrieve all users if no search query provided
            all_users = Author.objects.all().order_by('-displayName')
                
        follow_requests = Follow.objects.filter(object_of_follow__user = request.user, active = True)

        context = { 
            'user_list': all_users,
            'follow_requests': follow_requests,
        }

        

        return render(request, 'socialNetworking/find_friends.html', context)

class PostListView(View):
    def get(self, request, *args, **kwargs):
        toggle_option = request.GET.get('toggleOption')
        show_friends_posts = toggle_option == 'friends'  # Check if user selected "Friends" option

        posts = Post.objects.all().order_by('-published_at')
        print("ALL POSTS:",posts)

        friend_posts = []
        visible_posts = []
        currentUser_asAuthor = Author.objects.get(user=request.user)
        
        # for admin access
        if currentUser_asAuthor.is_approved:
            for post in posts:
                if post.visibility == 'PUBLIC':
                    visible_posts.append(post)
                    if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists() or post.author_of_posts == currentUser_asAuthor:
                        friend_posts.append(post)
                elif post.visibility == 'FRIENDS':
                    if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists() or post.author_of_posts == currentUser_asAuthor:
                        visible_posts.append(post)
                        friend_posts.append(post)
                elif post.visibility == 'UNLISTED' and request.user.is_authenticated:
                    if post.author_of_posts.user == request.user:
                        visible_posts.append(post)
                        friend_posts.append(post)
            
            if toggle_option == 'friends':
                posts = friend_posts
                template_name = 'socialNetworking/replace_post.html'
            elif toggle_option == 'all':
                posts = visible_posts
                template_name = 'socialNetworking/replace_post.html'
            else:
                posts = friend_posts
                template_name = 'socialNetworking/dashboard.html'
            
            form = PostForm()
            share_form = ShareForm()
            
            post_comments = {}
            for post in posts:
                comments = Comment.objects.filter(post=post).order_by('-published_at')
                post_comments[post.post_id] = comments

            follow_requests = Follow.objects.filter(object_of_follow__user = request.user, active = True)

            context = {
                'post_list': posts,
                'form': form,
                'post_comments': post_comments,
                'shareform': share_form,
                'follow_requests' : follow_requests
            }

        
            
            return render(request, template_name, context)
        else:
            return render(request, 'socialNetworking/waiting_approval.html')

    
class PostDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        # post = get_object_or_404(Post, pk=pk)
        post = Post.objects.get(pk=pk)
        print(post.author_of_posts)
        form = CommentForm()
        
        comments = Comment.objects.filter(post=post).order_by('-published_at')
  
        context = {
            'post': post,
            'form': form,
            'comments':comments
        }

        return render(request, 'socialNetworking/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        
        # form.fields['comment_author'].initial = Author.objects.get(user=request.user)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.comment_author = Author.objects.get(user=request.user)
            new_comment.post = post
            new_comment.save()
            form = CommentForm()

        
        comments = Comment.objects.filter(post=post).order_by('-published_at')
        
        
        print("HERE",comments)
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        

        return render(request, 'socialNetworking/post_detail.html', context)


class DashboardView(View):

    def get(self, request, *args, **kwargs):

        author = Author.objects.get(user= request.user)
        last_commit_fetch = author.lastCommitFetch
        if author.github:
            if not last_commit_fetch:
                try:
                    url = "https://api.github.com/search/commits?q=author:{} author-date:>={}&sort=author-date&order=desc".format(
                        author.github.split("/")[-1],
                        (datetime.now() + timedelta(weeks=-2)).strftime("%Y-%m-%d")
                    )
                    print(url)
                    response = requests.get(url).json()
                    for commit in response["items"]:
                        Post(
                            title = "Commit: " + commit["sha"],
                            type = "post",
                            origin = request.headers["Host"],
                            description = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["commit"]["message"]
                            ),
                            contentType = 'text/plain',
                            visibility = "Public",
                            published_at = commit["commit"]["author"]["date"],
                            author_of_posts = author
                        ).save()
                    author.lastCommitFetch = timezone.now()
                    author.save()
                except:
                    print("Unable to fetch the commits!")
            else:
                try:
                    url = "https://api.github.com/search/commits?q=author:{} author-date:>{}&sort=author-date&order=desc".format(
                        author.github.split("/")[-1],
                        author.lastCommitFetch.strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    print(url)
                    response = requests.get(url).json()
                    for commit in response["items"]:
                        Post(
                            title = "Commit: " + commit["sha"],
                            type = "post",
                            origin = request.headers["Host"],
                            description = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["commit"]["message"]
                            ),
                            contentType = 'text/plain',
                            visibility = "Public",
                            published_at = commit["commit"]["author"]["date"],
                            author_of_posts = author
                        ).save()
                    author.lastCommitFetch = timezone.now()
                    author.save()
                except:
                    print("Unable to fetch the commits!")

        shared_posts  = Post.objects.filter(
            shared_user=request.user,
            
        )
        
        posts = Post.objects.filter(author_of_posts__user=request.user).order_by('-published_at')
        form = PostForm()
        
        print("Shared",shared_posts)
        context = {
            'post_list': posts,
            'form': form,
            'author': author,
            'shared_posts':shared_posts,
        }

        return render(request, 'socialNetworking/profile_view.html', context)
    

class User_Profile(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        author = get_object_or_404(Author, pk=pk)
        last_commit_fetch = author.lastCommitFetch
        if author.github:
            if not last_commit_fetch:
                try:
                    url = "https://api.github.com/search/commits?q=author:{} author-date:>={}&sort=author-date&order=desc".format(
                        author.github.split("/")[-1],
                        (datetime.now() + timedelta(weeks=-2)).strftime("%Y-%m-%d")
                    )
                    print(url)
                    response = requests.get(url).json()
                    for commit in response["items"]:
                        Post(
                            title = "Commit: " + commit["sha"],
                            type = "post",
                            origin = request.headers["Host"],
                            description = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["commit"]["message"]
                            ),
                            contentType = 'text/plain',
                            visibility = "Public",
                            published_at = commit["commit"]["author"]["date"],
                            author_of_posts = author
                        ).save()
                    author.lastCommitFetch = timezone.now()
                    author.save()
                except:
                    print("Unable to fetch the commits!")
            else:
                try:
                    url = "https://api.github.com/search/commits?q=author:{} author-date:>{}&sort=author-date&order=desc".format(
                        author.github.split("/")[-1],
                        author.lastCommitFetch.strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    print(url)
                    response = requests.get(url).json()
                    for commit in response["items"]:
                        Post(
                            title = "Commit: " + commit["sha"],
                            type = "post",
                            origin = request.headers["Host"],
                            description = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["commit"]["message"]
                            ),
                            contentType = 'text/plain',
                            visibility = "Public",
                            published_at = commit["commit"]["author"]["date"],
                            author_of_posts = author
                        ).save()
                    author.lastCommitFetch = timezone.now()
                    author.save()
                except:
                    print("Unable to fetch the commits!")

        posts = Post.objects.filter(author_of_posts=author).order_by('-published_at')

        friend_posts = []
        visible_posts = []
        currentUser_asAuthor = Author.objects.get(user=request.user)

        if not Follower.objects.filter(followee=author, follower=currentUser_asAuthor).exists():
            for post in posts:
                if post.visibility == 'PUBLIC':
                    visible_posts.append(post)

            posts = visible_posts

        # for post in posts:
        #     if post.visibility == 'PUBLIC':
        #         visible_posts.append(post)
        #         if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():
        #             friend_posts.append(post)
        #     elif post.visibility == 'FRIENDS':
        #         if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():
        #             visible_posts.append(post)
        #             friend_posts.append(post)
        #     elif post.visibility == 'UNLISTED' and request.user.is_authenticated:
        #         if post.author_of_posts.user == request.user:
        #             visible_posts.append(post)
        #             friend_posts.append(post)

        form = PostForm()
        

        context = {
            'post_list': posts,
            'form': form,
            'author': author,
        }

        return render(request, 'socialNetworking/profile_view.html', context)
    
class PostEditView(UpdateView):
    model = Post
    fields = ['description',"visibility"]
    template_name = 'socialNetworking/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile')
    
    # def test_func(self):
    #     post = self.get_object()
    #     return self.request.user == post.author_of_posts

class SharedPostEditView(UpdateView):
    model = Post
    fields = ['shared_body',"visibility"]
    template_name = 'socialNetworking/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile')
    
    
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'socialNetworking/post_delete.html'
    success_url = reverse_lazy('profile')

    # def test_func(self):
    #     post = self.get_object()
    #     return self.request.user == post.author

class SharedPostDeleteView(DeleteView):
    model = Post
    template_name = 'socialNetworking/post_delete.html'
    success_url = reverse_lazy('profile')

    # def test_func(self):
    #     post = self.get_object()
    #     return self.request.user == post.author
   
    
class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'socialNetworking/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    # def test_func(self):
    #     comment = self.get_object()
    #     return self.request.user == comment.author
    
class ProfileEditView(UpdateView):
    def get(self, request, pk, *args, **kwargs):
        model = Author
        fields = ['displayName','github','url','host']
        template_name = 'socialNetworking/profile_edit.html'
        
        def get_success_url(self):
            pk = self.kwargs['pk']
            return reverse_lazy('profile')

        # profile = Author.objects.get(pk=pk)
        # user = profile.user
        # posts = Post.objects.filter(author_of_posts=user).order_by('-created_on')

        # context = {
        #     'user': user,
        #     'profile': profile,
        #     'posts': posts
        # }

        # return render(request, 'socialNetworking/profile_edit.html', context)

class AddLike(View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        author, created = Author.objects.get_or_create(user=request.user)
        

        if author in post.likes.all():
            print("Unliking")
            post.likes.remove(author)
        else:
            print("Liking")
            post.likes.add(author)
        

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
            
        author, created = Author.objects.get_or_create(user=request.user)
        if author in comment.likes.all():
            print("Unliking comment")
            comment.likes.remove(author)
        else:
            print("Liking comment")
            comment.likes.add(author)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    
def commentLike(request,post_pk, pk):
    # post = get_object_or_404(Post, pk=post_pk)
    author, created = Author.objects.get_or_create(user=request.user)
    comment = Comment.objects.get(pk=pk)
    current_likes = comment.num_likes
    liked = Like.objects.filter(author_like = author, like_comment = comment).count()
    
    if not liked:
        liked = Like.objects.create(author_like = author, like_comment = comment)
        current_likes+=1
    else:
        liked = Like.objects.filter(author_like = author, like_comment = comment).delete()
        current_likes-=1
    comment.num_likes=current_likes 
    comment.save()
    return HttpResponseRedirect(reverse_lazy('post-detail', kwargs={'pk': post_pk}))

class CommentReplyView(View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        
        author, created = Author.objects.get_or_create(user=request.user)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.comment_author = author
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        return redirect('post-detail', pk=post_pk)

class SharedPostView(View):
    def get(self, request, pk, *args, **kwargs):
        original_post = get_object_or_404(Post, pk=pk)
        shareForm = ShareForm()

        context = {
            'original_post': original_post,
            'shareform': shareForm
        }

        return render(request, 'socialNetworking/share_post.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        form = ShareForm(request.POST)
        author, created = Author.objects.get_or_create(user=request.user)
        
        if form.is_valid():
            new_post = Post(
					shared_body=self.request.POST.get('body'),
					description=original_post.description,
					author_of_posts=original_post.author_of_posts,
					published_at=original_post.published_at,
					shared_user=request.user,
					shared_on=timezone.now(),
				)
            new_post.save()
            
        return redirect('post-list')

def like(request, pk,*args, **kwargs):
    print("Hereee123")
    author, created = Author.objects.get_or_create(user=request.user)
    post = get_object_or_404(Post, pk=pk)
    current_likes = post.num_likes
    liked = Like.objects.filter(author_like = author, like_post = post).count()
    
    if not liked:
        liked = Like.objects.create(author_like = author, like_post = post)
        current_likes+=1
    else:
        liked = Like.objects.filter(author_like = author, like_post = post).delete()
        current_likes-=1
    post.num_likes=current_likes 
    post.save()
    
    return HttpResponseRedirect(reverse_lazy('post-list'))

@api_view(['GET'])
def authors(request):
    if request.method == 'GET':
        authors = Author.objects.all()

        if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
            page_size = request.GET.get('size')
            page_number = request.GET.get('page')
            paginated = Paginator(authors, page_size)
            authors = paginated.get_page(page_number)

        authors_serialized = AuthorSerializer(authors, many=True)

        output = {'type': 'authors', 'items': authors_serialized.data}

        return Response(output, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT'])
def authors_id(request, author_id):
    if Author.objects.filter(pk=author_id).exists():
        author = Author.objects.get(pk=author_id)

        if request.method == 'GET':
            author_serializer = AuthorSerializer(author)
            return Response(author_serializer.data, status=status.HTTP_200_OK)
         
        elif request.method == 'PUT':
            author_serializer = AuthorSerializer(author, data=request.data)
            if author_serializer.is_valid():
                author_serializer.save()
                return Response(author_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
            return Response({'error': "Author not found"}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
def followers(request, author_id):
    '''
        return all follower of author_id as json
    '''
    if Author.objects.filter(pk=author_id).exists():
        if request.method == 'GET':
            author = Author.objects.get(pk=author_id)
            followers = Author.objects.filter(follower_set__followee= author)
            followers_serialized = AuthorSerializer(followers, many=True)

            output = {'type': 'followers', 'items': followers_serialized.data}

            return Response(output, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND) 
    


@api_view(['GET', 'PUT', 'DELETE'])
def followers_id(request, author_id, foreign_author_id):
    if Author.objects.filter(pk=author_id).exists() and Author.objects.filter(pk=foreign_author_id).exists():
        followee = Author.objects.get(pk=author_id)
        follower = Author.objects.get(pk=foreign_author_id)
        obj_follow = Follower.objects.get(followee=followee, follower=follower)
        if request.method == 'GET':
            follower_serializer = FollowerSerializer(obj_follow)
            return Response(follower_serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            follower_serializer = FollowerSerializer(request.data)
            if follower_serializer.is_valid():
                follower_serializer.save()
                return Response(follower_serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            obj_follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        if not Author.objects.filter(pk=author_id).exists():
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Follower not found'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET', 'POST'])
def posts(request, author_id):
    if Author.objects.filter(pk=author_id).exists():

        if request.method == 'GET':
            author = Author.objects.get(pk=author_id)
            posts = Post.objects.filter(author_of_posts=author).order_by('-published_at')

            if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
                page_size = request.GET.get('size')
                page_number = request.GET.get('page')
                paginated = Paginator(posts, page_size)
                posts = paginated.get_page(page_number)

            posts_serialized = TextPostSerializer(posts, many=True)

            output = {'type': 'posts', 'items': posts_serialized.data}

            return Response(output, status=status.HTTP_200_OK)
    
        elif request.method == 'POST':
            return
        
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'DELETE'])
def posts_id(request, author_id, post_id):
    if Author.objects.filter(pk=author_id).exists() and Post.objects.filter(pk=post_id).exists():
        post = Post.objects.get(pk=post_id)    

        if request.method == 'GET':
            post_serializer = TextPostSerializer(post)
            return Response(post_serializer.data, status=status.HTTP_200_OK)
    
        elif request.method == 'PUT':
            post_serializer = TextPostSerializer(post, data=request.data)
            if post_serializer.is_valid():
                post_serializer.save()
                return Response(post_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def image(request, author_id, post_id):
    return


@api_view(['GET', 'POST'])
def comments(request, author_id, post_id):
    if Author.objects.filter(pk=author_id).exists() and Post.objects.filter(pk=post_id).exists():

        if request.method == 'GET':
            post_data = Post.objects.get(pk=post_id)
            comments = Comment.objects.filter(post=post_data).order_by('-published_at')

            if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
                page_size = request.GET.get('size')
                page_number = request.GET.get('page')
                paginated = Paginator(comments, page_size)
                comments = paginated.get_page(page_number)

            comments_serialized = CommentSerializer(comments, many=True)

            output = {'type': 'comments', 'items': comments_serialized.data}

            return Response(output, status=status.HTTP_200_OK)
    
        elif request.method == 'POST':
            return
        
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def posts_likes(request, author_id, post_id):
    return


@api_view(['GET'])
def comments_likes(request, author_id, post_id, comment_id):
    return


@api_view(['GET'])
def liked(request, author_id):
    return

@api_view(['GET', 'POST', 'DELETE'])
def inbox(request, author_id):
    if Author.objects.filter(pk=author_id).exists():
        author = Author.objects.get(pk=author_id)

        if request.method == 'GET':
            inb_Posts = author.postInbox.all()
            inb_Comments = author.commentInbox.all()
            inb_Likes = author.likeInbox.all()
            inb_Follows = author.followInbox.all()

            ser_inb_Posts = TextPostSerializer(inb_Posts, many=True)
            ser_inb_Comments = CommentSerializer(inb_Comments, many=True)
            ser_inb_Likes = LikeSerializer(inb_Likes, many=True)
            ser_inb_Follows = FollowSerializer(inb_Follows, many=True)

            data_inb_Posts = ser_inb_Posts.data
            data_inb_Comments = ser_inb_Comments.data
            data_inb_Likes = ser_inb_Likes.data
            data_inb_Follows = ser_inb_Follows.data

            inbox_list = data_inb_Posts + data_inb_Comments + data_inb_Likes + data_inb_Follows
            inbox_list = sorted(inbox_list, key=lambda x: x['published'], reverse=True)

            output = {'type': 'inbox', 'author': getattr(author, 'url'), 'items': inbox_list}

            return Response(output, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            
            if request.data.get('type') == 'post':
                pass

            elif request.data.get('type') == 'comment':
                pass

            elif request.data.get('type') == 'like':
                like_author = request.data.get('author')

                if not Author.objects.filter(url=like_author.get('id')).exists():
                    author_serializer = AuthorSerializer(data=like_author)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                like_serializer = LikeSerializer(data=request.data)
                if like_serializer.is_valid():
                    like_serializer.save()
                else:
                    return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                

                like_obj = Like.objects.get(author_like=None)
                like_obj.author_like = Author.objects.get(url=like_author.get('id'))
                like_obj.save()
                
                author.likeInbox.add(like_obj)
                
                output = LikeSerializer(like_obj)

                return Response(output.data, status=status.HTTP_201_CREATED)

            elif request.data.get('type') == 'follow':
                pass

        elif request.method == 'DELETE':
            pass

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST']) 
def send_friend_request(request, *args, **kwargs):
    user = request.user
    context = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            try:
                receiver = Author.objects.get(pk=user_id)
                author = Author.objects.get(user=user)
                
                # Check if an active follow request already exists
                existing_request = Follow.objects.filter(actor=author, object_of_follow=receiver, active=True).exists()
                if existing_request:
                    context['result'] = "follow request exists"
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
                
                # Create a new follow request
                friend_request = Follow.objects.create(actor=author, object_of_follow=receiver)
                context['result'] = "Successful"
                return Response(context, status=status.HTTP_200_OK)
            
            except Author.DoesNotExist:
                context['result'] = "Receiver user not found"
                return Response(context, status=status.HTTP_404_NOT_FOUND)
        
        else:
            context['result'] = "Invalid data"
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        context['result'] = "Authentication required"
        return Response(context, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST']) 
def accept_friend_request(request, *args, **kwargs):
    user = request.user
    context = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            try:

                actor = Author.objects.get(pk=user_id)
                object_of_follow = Author.objects.get(user=user)
                print(actor)
                follow_request = Follow.objects.filter(actor=actor, object_of_follow=object_of_follow, active=True).first()

                if follow_request:

                    # Check if there's already a follower entry
                    if Follower.objects.filter(follower=actor, followee=object_of_follow).exists():
                        context['result'] = "You are already following this user"
                        return Response(context, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Create Follower object
                    follower = Follower.objects.create(follower=actor, followee=object_of_follow)
                    serializer = FollowerSerializer(follower)
                    context['result'] = "Successful"
                    # Deactivate the friend request
                    follow_request.active = False
                    follow_request.save()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    context['result'] = "Friend request not found or already accepted"
                    return Response(context, status=status.HTTP_404_NOT_FOUND)
            except Author.DoesNotExist:
                context['result'] = "Actor user not found"
                return Response(context, status=status.HTTP_404_NOT_FOUND)
        else:
            context['result'] = "Invalid data"
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
    else:
        context['result'] = "Authentication required"
        return Response(context, status=status.HTTP_401_UNAUTHORIZED)