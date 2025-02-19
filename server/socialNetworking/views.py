from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Case, When, Value, Max
import json
from urllib.parse import unquote

# drf_spectaculars
from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer, OpenApiParameter
from rest_framework import serializers

from django.utils import timezone
from django.views import View
from .models.posts import Post
from .models.comments import Comment
from .models.followers import Follower
from .models.follow import Follow
from .models.likes import Like
from .models.nodes import Node
from .models.approval import Approval
from .forms import PostForm, CommentForm, ShareForm, DraftForm
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
  LikeSerializer,
  ImagePostSerializer
  )
from rest_framework.response import Response
from rest_framework import status

import base64
import requests
from requests.auth import HTTPBasicAuth
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
        
        form = PostForm(request.POST, request.FILES)
        share_form = ShareForm()

        if form.is_valid():
             # Retrieve the User instance associated with the request
            user_instance = request.user if isinstance(request.user, User) else User.objects.get(username=request.user)

            # Retrieve or create Author instance associated with the User
            author_instance = Author.objects.get(user=user_instance)
            new_post = form.save(commit=False)
            new_post.author_of_posts = author_instance
            new_post.url = author_instance.url + "/posts/" + str(new_post.post_id)
            new_post.source = new_post.url
            new_post.origin = new_post.url
            content_type = form.cleaned_data.get('contentType')
            if content_type in ['image/png;base64', 'image/jpeg;base64','application/base64']:
                # For images, convert to base64 and store as bytes
                if 'content' in request.FILES:
                    image = request.FILES['content']
                    new_post.content = image.read()
            else:
                # For text/markdown, encode as utf-8 to store as bytes
                if 'content' in request.POST:
                    new_post.content = request.POST['content'].encode('utf-8')
            
            # if new_post.contentType in ['image/png;base64', 'image/jpeg;base64']:
            #     # Handle image file; convert to base64
            #     if 'content' in request.FILES:
            #         image = request.FILES['content']
            #         new_post.content = base64.b64encode(image.read())
            #     elif new_post.contentType == 'application/base64':
            #     # If content is text but encoded in base64, decode it for storage
            #     # Assuming you want to store decoded content; otherwise, remove decoding
            #         decoded_content = base64.b64decode(request.POST['content'])
            #         new_post.content = decoded_content
            # elif new_post.contentType in ['text/markdown', 'text/plain']:
            # # Handle text and markdown files
            #     if 'content' in request.FILES:
            #         text_file = request.FILES['content']
            #         new_post.content = text_file.read()
            
            new_post.save()

            # HTTP Request to POST new public post to inbox of followers
            if new_post.visibility == 'PUBLIC':
                follower_list = Author.objects.filter(follower_set__followee=author_instance)
                for flwr in follower_list:
                    print(flwr.host)
                    node = Node.objects.get(host_url=flwr.host)
                    print(node.username_out)
                    print(node.password_out)
                    output = None
                    if new_post.contentType == 'text/plain' or new_post.contentType == 'text/markdown':
                        output = TextPostSerializer(new_post)
                    else:
                        output = ImagePostSerializer(new_post)
                    print(output.data)
                    response = requests.post(flwr.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
                    print(response.status_code)
            
            # TODO: HTTP Requests to POST new friends-only post to inbox of friends
            elif new_post.visibility == 'FRIENDS':
                friends_list = Author.objects.filter(follower_set__followee=author_instance, followee_set__follower=author_instance)
                for friend in friends_list:
                    print(friend.host)
                    node = Node.objects.get(host_url=friend.host)
                    print(node.username_out)
                    print(node.password_out)
                    output = None
                    if new_post.contentType == 'text/plain' or new_post.contentType == 'text/markdown':
                        output = TextPostSerializer(new_post)
                    else:
                        output = ImagePostSerializer(new_post)
                    print(output.data)
                    response = requests.post(friend.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
                    print(response.status_code)

            # Create a new, empty form after successfully saving the post
            form = PostForm()
            return redirect('post-list')
            
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

        # TODO: HTTP Requests to GET list of authors from remote servers, then add them to database
        # (Maybe should be somewhere else where it is called earlier and less often)

        nodes = Node.objects.exclude(host_url=request.build_absolute_uri('/'))
        remote_authors = []
        for node in nodes:
            response = requests.get(node.api_url + 'authors/?page=1&size=100', auth=HTTPBasicAuth(node.username_out, node.password_out))
            print(response.status_code)
            json_data = response.json()
            remote_authors = remote_authors + json_data.get('items')
        for author in remote_authors:
            if not Author.objects.filter(url=author.get('id')).exists():
                author_serializer = AuthorSerializer(data=author)
                if author_serializer.is_valid():
                    author_serializer.save()
                else:
                    print('Serializer invalid')
                    print(author)
                    
        
        if query:
            # Filter users based on the search query
            all_users = Author.objects.filter(displayName__icontains=query).order_by('-displayName')
        else:
            # Retrieve all users if no search query provided
            all_users = Author.objects.all().order_by('-displayName')
                
        follow_requests = Follow.objects.filter(object_of_follow__user = request.user, active = True)
        sent_follow_requests = Follow.objects.filter(actor__user = request.user, active = True)
        sent_requests_set = set(follow.object_of_follow_id for follow in sent_follow_requests)  



        followers = Follower.objects.filter(follower__user=request.user)
        following_set = set(follower_user.followee_id for follower_user in followers)


        context = { 
            'user_list': all_users,
            'follow_requests': follow_requests,             
            'sent_requests_set': sent_requests_set,
            'following_set' : following_set,

        }

        

        return render(request, 'socialNetworking/find_friends.html', context)

class PostListView(View):
    def get(self, request, *args, **kwargs):
        toggle_option = request.GET.get('toggleOption')
        show_friends_posts = toggle_option == 'friends'  # Check if user selected "Friends" option
        shared_or_published = Case(
            When(shared_on__isnull=False, then=F('shared_on')),
            default=F('published_at'),
        )
        posts_with_shared_or_published = Post.objects.annotate(shared_or_published=shared_or_published)
        posts = posts_with_shared_or_published.order_by('-shared_or_published')

        # posts = Post.objects.all().order_by('-published_at').exclude(visibility=Post.VisibilityChoices.UNLISTED)

        friend_posts = []
        visible_posts = []
        currentUser_asAuthor = Author.objects.get(user=request.user)
        
        # for admin access 
        
        # check approval if its required by admin
        approval_instance, created = Approval.objects.get_or_create(id=1, defaults={'require_approval': True})
        
        # check if approval is required
        if approval_instance.require_approval:
            if currentUser_asAuthor.is_approved:
                for post in posts:
                    if post.visibility == 'PUBLIC':
                        visible_posts.append(post)
                        #  NO NEED TO ADD TO FRIENDS ONLY IF ITS A PUBLIC POST
                        if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():
                            friend_posts.append(post)
                    # dont add users friends only posts
                    elif post.visibility == 'FRIENDS':
                        if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():

                            if Follower.objects.filter(followee=currentUser_asAuthor, follower=post.author_of_posts).exists():
                                # visible_posts.append(post)
                                friend_posts.append(post)
                        elif post.author_of_posts == currentUser_asAuthor:
                            friend_posts.append(post)
                    # elif post.visibility == 'UNLISTED' and request.user.is_authenticated:
                    #     if post.author_of_posts.user == request.user:
                    #         visible_posts.append(post)
                    #         friend_posts.append(post)
                
                print(toggle_option)
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
                new = currentUser_asAuthor.followInbox
                print(new)
                context = {
                    'post_list': posts,
                    'form': form,
                    'post_comments': post_comments,
                    'shareform': share_form,
                    'follow_requests' : follow_requests,
                    'author': Author.objects.get(user= request.user)
                }
                
                return render(request, template_name, context)
            else:
                return render(request, 'socialNetworking/waiting_approval.html')

        # no approval is required - direct access to the system by the user
        else:
            for post in posts:
                    if post.visibility == 'PUBLIC':
                        visible_posts.append(post)
                        # NO NEED TO ADD A PUBLIC POST TO FRIENDS ONLY
                        if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():
                            friend_posts.append(post)
                    elif post.visibility == 'FRIENDS':
                        if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists():
                            if Follower.objects.filter(followee=currentUser_asAuthor, follower=post.author_of_posts).exists():
                                # visible_posts.append(post)
                                friend_posts.append(post)
                        elif post.author_of_posts == currentUser_asAuthor:
                            friend_posts.append(post)
                    # elif post.visibility == 'UNLISTED' and request.user.is_authenticated:
                    #     if post.author_of_posts.user == request.user:
                    #         visible_posts.append(post)
                    #         friend_posts.append(post)
                
            if toggle_option == 'friends':
                posts = friend_posts
                print(posts)
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
            new = currentUser_asAuthor.followInbox
            print(new)
            context = {
                'post_list': posts,
                'form': form,
                'post_comments': post_comments,
                'shareform': share_form,
                'follow_requests' : follow_requests,
                'author': Author.objects.get(user= request.user)
            }
            
            return render(request, template_name, context)
        # else:
        #     return render(request, 'socialNetworking/waiting_approval.html')

    
class PostDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        # post = get_object_or_404(Post, pk=pk)
        post = Post.objects.get(pk=pk)
        print(post.author_of_posts)
        form = CommentForm()

        # TODO: Fetch comments if post is foreign and PUBLIC
        if not post.author_of_posts.host == request.build_absolute_uri('/'):
            node = Node.objects.get(host_url=post.author_of_posts.host)
            response = requests.get(post.url + '/comments?page=1&size=15', auth=HTTPBasicAuth(node.username_out, node.password_out))
            print(response.status_code)
            json_data = response.json()
            comment_list = json_data.get('comments')
            if not comment_list:
                comment_list = []
            for cmnt in comment_list:
                comment_auth = cmnt.get('author')

                if not Author.objects.filter(url=comment_auth.get('id')).exists():
                    author_serializer = AuthorSerializer(data=comment_auth)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        print('Serializer invalid')
                        print(comment_auth)
                
                if not Comment.objects.filter(url=cmnt.get('id')).exists():    
                    comment_serializer = CommentSerializer(data=cmnt)
                    if comment_serializer.is_valid():
                        comment_serializer.save()
                    else:
                        print('Serializer invalid')
                        print(cmnt)
                    
                    comment_obj = Comment.objects.get(comment_author=None)
                    comment_obj.comment_author = Author.objects.get(url=comment_auth.get('id'))
                    comment_obj.post = post
                    comment_obj.save()
        
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
            new_comment.url = post.url + '/comments/' + str(new_comment.comment_id)
            new_comment.save()
            form = CommentForm()

            # HTTP Request to POST new comment to inbox of post author
            print(post.author_of_posts.host)
            node = Node.objects.get(host_url=post.author_of_posts.host)
            print(node.username_out)
            print(node.password_out)
            output = CommentSerializer(new_comment)
            print(output.data)
            response = requests.post(post.author_of_posts.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
            print(response.status_code)
        
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

        # Get the author and the last time the author's commits were fetched
        author = Author.objects.get(user= request.user)
        last_commit_fetch = author.lastCommitFetch

        # If the author has provided a github URL
        if author.github:

            # Get the follower of the author to send new posts to (if needed)
            follower_list = Author.objects.filter(follower_set__followee=author)
            print()
            print(follower_list)
            print()

            # Fetch the last 2 weeks commits if no fetch has ever been made
            if not last_commit_fetch:
                try:
                    url = "https://api.github.com/search/commits?q=author:{} author-date:>={}&sort=author-date&order=desc".format(
                        author.github.split("/")[-1],
                        (datetime.now() + timedelta(weeks=-2)).strftime("%Y-%m-%d")
                    )
                    print(url)
                    response = requests.get(url).json()
                    author.lastCommitFetch = timezone.now()
                    author.save()

                    # Create new post for all commits and distribute to followers
                    for commit in response["items"]:

                        # Create new post based on the commit
                        new_post = Post(
                            title = "[{}]: {}".format(commit["repository"]["name"], commit["commit"]["message"]),
                            type = "post",
                            origin = request.headers["Host"],
                            description = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["sha"]
                            ),
                            content = "[{}]: {}".format(
                                commit["repository"]["name"],
                                commit["sha"]
                            ).encode('utf-8'),
                            contentType = 'text/plain',
                            visibility = "PUBLIC",
                            published_at = commit["commit"]["author"]["date"],
                            author_of_posts = author
                        )
                        new_post.url = author.url + "/posts/" + str(new_post.post_id)
                        new_post.origin = new_post.url
                        new_post.source = new_post.url
                        new_post.save()

                        # POST the new post to followers
                        for flwr in follower_list:
                            node = Node.objects.get(host_url=flwr.host)
                            output = TextPostSerializer(new_post)
                            print(output)
                            response = requests.post(flwr.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
                            print(response.json())

                except:
                    print("Unable to fetch the commits or POST to followers!")

            # Fetch all commits since the last fetch (restriction is every 5 seconds)
            else:
                try:
                    if ((author.lastCommitFetch + timedelta(seconds=5)) < timezone.now()):
                        url = "https://api.github.com/search/commits?q=author:{} author-date:>{}&sort=author-date&order=desc".format(
                            author.github.split("/")[-1],
                            author.lastCommitFetch.strftime("%Y-%m-%dT%H:%M:%S")
                        )
                        print(url)
                        response = requests.get(url).json()
                        author.lastCommitFetch = timezone.now()
                        author.save()

                        # Create new post for all commits and distribute to followers
                        for commit in response["items"]:

                            # Create new post based on the commit
                            new_post = Post(
                                title = "[{}]: {}".format(commit["repository"]["name"], commit["commit"]["message"]),
                                type = "post",
                                origin = request.headers["Host"],
                                description = "[{}]: {}".format(
                                    commit["repository"]["name"],
                                    commit["sha"]
                                ),
                                content = "[{}]: {}".format(
                                    commit["repository"]["name"],
                                    commit["sha"]
                                ).encode('utf-8'),
                                contentType = 'text/plain',
                                visibility = "PUBLIC",
                                published_at = commit["commit"]["author"]["date"],
                                author_of_posts = author
                            )
                            new_post.url = author.url + "/posts/" + str(new_post.post_id)
                            new_post.origin = new_post.url
                            new_post.source = new_post.url
                            new_post.save()

                            # POST the new post to followers
                            for flwr in follower_list:
                                node = Node.objects.get(host_url=flwr.host)
                                output = TextPostSerializer(new_post)
                                print(output)
                                response = requests.post(flwr.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
                                print(response.json())

                except:
                    print("Unable to fetch the commits or POST to followers!")

        shared_posts  = Post.objects.filter(
            shared_user=request.user,
        )
        
        unlisted_post = Post.objects.filter(
            author_of_posts=author,visibility=Post.VisibilityChoices.UNLISTED
        )

        draft = DraftForm(request.POST or None, instance=author)
        
        posts = Post.objects.filter(author_of_posts__user=request.user).exclude(visibility=Post.VisibilityChoices.UNLISTED).order_by('-published_at')
        form = PostForm()
        
        print("Shared",shared_posts)
        context = {
            'post_list': posts,
            'form': form,
            'author': author,
            'shared_posts':shared_posts,
            'draft': draft,
            'myProfile': True,
            'unlisted_posts':unlisted_post,
        }

        return render(request, 'socialNetworking/profile_view.html', context)
    
    def post(self, request, *args, **kwargs):

        # Get the author that makes the update request
        author = Author.objects.get(id= request.POST.get("id"))

        # Handle an update request
        if ('Update' in request.POST):

            # Handle display name
            if (request.POST.get("draftDisplayName").strip()):
                author.displayName = request.POST.get("draftDisplayName")
                author.draftDisplayName = request.POST.get("draftDisplayName")
            
            # Handle profile image
            if (request.FILES.get("draftProfileImage")):
                author.draftProfileImage = request.FILES.get("draftProfileImage")
                author.profileImagePicture = request.FILES.get("draftProfileImage")
                author.save()
                author.profileImage = author.host + author.profileImagePicture.url[1:]
            else:
                author.draftProfileImage = None
                author.profileImagePicture = None
                author.profileImage = None

            # Handle github URL
            if (request.POST.get("draftGithub").strip()):
                try:
                    author.github = request.POST.get("draftGithub")
                    author.draftGithub = request.POST.get("draftGithub")
                except:
                    print("Invalid github URL!")
            else:
                author.github = None
                author.draftGithub = None
                author.lastCommitFetch = None

            author.save()

        # Handle a local save request
        elif ('Save as Draft' in request.POST):

            # Handle display name
            if (request.POST.get("draftDisplayName").strip()):
                author.draftDisplayName = request.POST.get("draftDisplayName")

            # Handle profile image
            if (request.FILES.get("draftProfileImage")):
                author.draftProfileImage = request.FILES.get("draftProfileImage")
            else:
                author.draftProfileImage = None

            # Handle github URL
            if (request.POST.get("draftGithub").strip()):
                try:
                    author.draftGithub = request.POST.get("draftGithub")
                except:
                    print("Invalid github URL!")
            else:
                author.draftGithub = None

            author.save()

        return redirect("profile")

class User_Profile(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        author = get_object_or_404(Author, pk=pk)

        posts = Post.objects.filter(author_of_posts=author).order_by('-published_at')

        myProfile = author.user == request.user
        if (myProfile):
            return redirect('profile')

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

        follow_requests = Follow.objects.filter(object_of_follow__user = request.user, active = True)
        sent_follow_requests = Follow.objects.filter(actor__user = request.user, active = True)
        sent_requests_set = set(follow.object_of_follow_id for follow in sent_follow_requests)  



        followers = Follower.objects.filter(follower__user=request.user)
        following_set = set(follower_user.followee_id for follower_user in followers)

        unlisted_post = Post.objects.filter(
            author_of_posts=author,visibility=Post.VisibilityChoices.UNLISTED
        )
        
        shared_posts  = Post.objects.filter(
            shared_user=request.user,
        )

        context = {
            # 'user_list': all_users,
            'follow_requests': follow_requests,             
            'sent_requests_set': sent_requests_set,
            'following_set' : following_set,
            'myProfile': False,
            'post_list': posts,
            'form': form,
            'author': author,
            'unlisted_posts':unlisted_post,
            'shared_posts':shared_posts,
        }

        return render(request, 'socialNetworking/profile_view.html', context)
    
class PostEditView(UpdateView):
    model = Post
    fields = ['title',"visibility"]
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

class UnlistedPostEditView(UpdateView):
    model = Post
    fields = ['title',"visibility"]
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
        liked = Like.objects.create(summary = author.displayName + ' likes your comment', author_like = author, like_comment = comment, object = comment.url)
        current_likes+=1

        # HTTP Request to POST new comment like to inbox of comment author
        print(comment.comment_author.host)
        node = Node.objects.get(host_url=comment.comment_author.host)
        print(node.username_out)
        print(node.password_out)
        output = LikeSerializer(liked)
        print(output.data)
        response = requests.post(comment.comment_author.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
        print(response.status_code)

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
                    title=original_post.title,
                    url=original_post.url,
                    source=original_post.source,
                    origin=original_post.origin,
					description=original_post.description,
                    contentType=original_post.contentType,
                    content=original_post.content,
                    visibility=original_post.visibility,
					author_of_posts=original_post.author_of_posts,
					published_at=original_post.published_at,
					shared_user=request.user,
					shared_on=timezone.now(),
				)
            new_post.url = new_post.author_of_posts.url + '/posts/' + str(new_post.post_id)
            new_post.save()

            follower_list = Author.objects.filter(follower_set__followee=author)
            for flwr in follower_list:
                print(flwr.host)
                node = Node.objects.get(host_url=flwr.host)
                print(node.username_out)
                print(node.password_out)
                output = None
                if new_post.contentType == 'text/plain' or new_post.contentType == 'text/markdown':
                    output = TextPostSerializer(new_post)
                else:
                    output = ImagePostSerializer(new_post)
                print(output.data)
                response = requests.post(flwr.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
                print(response.status_code)
            
        return redirect('post-list')

# def like(request, pk,*args, **kwargs):
#     print("Hereee123")
#     author, created = Author.objects.get_or_create(user=request.user)
#     post = get_object_or_404(Post, pk=pk)
#     current_likes = post.num_likes
#     liked = Like.objects.filter(author_like = author, like_post = post).count()
    
#     if not liked:
#         liked = Like.objects.create(author_like = author, like_post = post)
#         current_likes+=1
#     else:
#         liked = Like.objects.filter(author_like = author, like_post = post).delete()
#         current_likes-=1
#     post.num_likes=current_likes 
#     post.save()
    
#     return HttpResponseRedirect(reverse_lazy('post-list'))
@extend_schema(
    methods=['POST'],  
    summary="Like or Unlike a Post",
    description="Performs a like action on a post by the current user. If the post is already liked by the user, it unlikes it.",
    request=None,  
    responses={200: None},
    tags=['Likes']
)    
@api_view(['POST'])
def likeAction(request, post_pk):
    if request.method == 'POST':
        author, created = Author.objects.get_or_create(user=request.user)
        post = get_object_or_404(Post, pk=post_pk)
        current_likes = post.num_likes
        liked = Like.objects.filter(author_like = author, like_post = post).count()
        if not liked:
            liked = Like.objects.create(author_like = author, like_post = post, object = post.url)
            current_likes+=1

            # HTTP Request to POST new post like to inbox of post author
            print(post.author_of_posts.host)
            node = Node.objects.get(host_url=post.author_of_posts.host)
            print(node.username_out)
            print(node.password_out)
            output = LikeSerializer(liked)
            print(output.data)
            response = requests.post(post.author_of_posts.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out))
            print(response.status_code)

        else:
            liked = Like.objects.filter(author_like = author, like_post = post).delete()
            current_likes-=1
        post.num_likes=current_likes 
        post.save()
        data = {
            "num_likes": post.num_likes,
        }
 
        return JsonResponse(data, status=200)
    
@extend_schema_view(
    get=extend_schema(
        summary="List Authors",
        responses={200: AuthorSerializer(many=True)},
        description="Retrieves a list of authors, optionally paginated."
    )
)
@api_view(['GET'])
def authors(request):
    if request.method == 'GET':
        authors = Author.objects.exclude(user=None)

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

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve an Author",
        responses={200: AuthorSerializer},
        description="Retrieves detailed information about a specific author by their ID."
    ),
    put=extend_schema(
        summary="Update an Author",
        request=AuthorSerializer,
        responses={201: AuthorSerializer},
        description="Updates an existing author's details. Returns the updated author information."
    )
)
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


@extend_schema_view(
    get=extend_schema(
        summary="List Followers",
        responses={200: FollowerSerializer(many=True)},
        description="Returns all followers of a specified author by the author's ID.",
        tags=['Followers']
    )
)
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
    

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Follower Relationship",
        responses={200: AuthorSerializer},
        description="Retrieves detailed information about a specific follower relationship.",
        tags=['Followers']
    ),
    put=extend_schema(
        summary="Accept Follower Request",
        responses={
            201: AuthorSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            404: {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        description="Accepts a follower request between the specified authors.",
        tags=['Followers'],
        request=AuthorSerializer,
    ),
    delete=extend_schema(
        summary="Remove Follower Relationship",
        responses={
            204: None,
            404: {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        description="Deletes a follower relationship between the specified authors.",
        tags=['Followers']
    )
)
@api_view(['GET', 'PUT', 'DELETE'])
def followers_id(request, author_id, foreign_author_id):
    if Author.objects.filter(pk=author_id):
        followee = Author.objects.get(pk=author_id)
        decoded_fid = unquote(foreign_author_id)

        if Author.objects.filter(url=decoded_fid).exists():
            follower = Author.objects.get(url=decoded_fid)

            if request.method == 'GET':
                if Follower.objects.filter(followee=followee, follower=follower).exists():
                    follower_obj = Follower.objects.get(followee=followee, follower=follower)
                    f_obj_str = follower_obj.__str__()
                    followee_ser = AuthorSerializer(followee)
                    follower_ser = AuthorSerializer(follower)

                    output = {'type': 'Follow', 'summary': f_obj_str, 'actor': follower_ser.data, 'object': followee_ser.data}

                    return Response(output, status=status.HTTP_200_OK)
                
                else:
                    return Response({'error': 'Foreign author not a follower'}, status=status.HTTP_404_NOT_FOUND)
            
            elif request.method == 'PUT':
                if not Follower.objects.filter(followee=followee, follower=follower).exists():
                    follower_obj = Follower.objects.create(follower=follower, followee=followee)
                    followee_ser = AuthorSerializer(followee)
                    follower_ser = AuthorSerializer(follower)
                    output = {'type': 'Follow', 'summary': f_obj_str, 'actor': follower_ser.data, 'object': followee_ser.data}

                    return Response(output, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Foreign author already a follower'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif request.method == 'DELETE':
                if Follower.objects.filter(followee=followee, follower=follower).exists():
                    follower_obj = Follower.objects.get(followee=followee, follower=follower)
                    follower_obj.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'error': 'Foreign author not a follower'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'error': 'Foreign author not found'}, status=status.HTTP_404_NOT_FOUND)

    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    get=extend_schema(
        summary="List Posts by Author",
        responses={200: TextPostSerializer(many=True)},
        description="Retrieves a list of posts made by a specified author, optionally paginated.",
        tags=['Posts']
    ),
    post=extend_schema(
        summary="Create a Post for an Author",
        request=TextPostSerializer,
        responses={201: TextPostSerializer},
        description="Creates a new post for the specified author.",
        tags=['Posts']
    )
)
@api_view(['GET', 'POST'])
def posts(request, author_id):
    if Author.objects.filter(pk=author_id).exists():
        author = Author.objects.get(pk=author_id)

        if request.method == 'GET':
            text_posts = Post.objects.filter(author_of_posts=author, contentType="text/plain", visibility="PUBLIC") | Post.objects.filter(author_of_posts=author, contentType="text/markdown", visibility="PUBLIC")
            image_posts = Post.objects.filter(author_of_posts=author, contentType="image/png;base64", visibility="PUBLIC") | Post.objects.filter(author_of_posts=author, contentType="image/jpeg;base64", visibility="PUBLIC")

            text_posts_ser = TextPostSerializer(text_posts, many=True)
            image_posts_ser = ImagePostSerializer(image_posts, many=True)

            text_posts_data = text_posts_ser.data
            image_posts_data = image_posts_ser.data

            posts_list = text_posts_data + image_posts_data
            posts_list = sorted(posts_list, key=lambda x: x['published'], reverse=True)

            if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
                page_size = request.GET.get('size')
                page_number = request.GET.get('page')
                paginated = Paginator(posts_list, page_size)
                page = paginated.get_page(page_number)
                posts_list = page.object_list

            output = {'type': 'posts', 'items': posts_list}

            return Response(output, status=status.HTTP_200_OK)
    
        elif request.method == 'POST':
            cont_type = request.data.get('contentType')
            post_serializer = None

            if cont_type == 'text/plain' or cont_type == 'text/markdown':
                post_serializer = TextPostSerializer(data=request.data)
            else:
                post_serializer = ImagePostSerializer(data=request.data)

            if post_serializer.is_valid():
                post_serializer.save()
            else:
                return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            post_obj = Post.objects.get(author_of_posts=None)
            post_obj.author_of_posts = author
            post_obj.url = author.url + "/posts/" + str(post_obj.post_id)
            post_obj.source = post_obj.url
            post_obj.origin = post_obj.url
            post_obj.save()

            output = None
            if cont_type == 'text/plain' or cont_type == 'text/markdown':
                output = TextPostSerializer(post_obj)
            else:
                output = ImagePostSerializer(post_obj)
            
            return Response(output.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a Post",
        responses={
            200: None  
        },
        description="Retrieves detailed information about a specific post by its ID, dynamically choosing the serializer based on the post's content type.",
        tags=['Posts']
    ),
    put=extend_schema(
        summary="Update a Post",
        request=TextPostSerializer,  
        responses={201: TextPostSerializer},
        description="Updates an existing text post's details. Note: This example assumes text content; you may need to handle image posts separately.",
        tags=['Posts']
    ),
    delete=extend_schema(
        summary="Delete a Post",
        responses={204: None},
        description="Deletes a specific post by its ID.",
        tags=['Posts']
    )
)
@api_view(['GET', 'PUT', 'DELETE'])
def posts_id(request, author_id, post_id):
    if Author.objects.filter(pk=author_id).exists() and Post.objects.filter(pk=post_id).exists():
        post = Post.objects.get(pk=post_id)    

        if request.method == 'GET':
            post_serializer = None
            if post.contentType == 'text/plain' or post.contentType == 'text/Markdown':
                post_serializer = TextPostSerializer(post)
            else:
                post_serializer = ImagePostSerializer(post)
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

@extend_schema(
    methods=['GET'], 
    summary="Retrieve an Image Post",
    description="Returns the image of a specific post by an author in binary format. Only supports 'image/png;base64' and 'image/jpeg;base64' content types.",
    responses={
        200: None,  
        400: None,  
    },
    tags=['Posts'],
)
@api_view(['GET'])
def image(request, author_id, post_id):
    
    if request.method == "GET":
        if Author.objects.filter(id=author_id).exists():
            author = Author.objects.get(id=author_id)
            if Post.objects.filter(author_of_posts=author, post_id=post_id).exists():
                post = Post.objects.get(author_of_posts=author, post_id=post_id)
                if post.contentType in ["image/png;base64", "image/jpeg;base64"]:
                    return HttpResponse(post.content, status=status.HTTP_200_OK, content_type=post.contentType)
                else:
                    return JsonResponse({'result': 'Post is not an image'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'result': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({'result': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@extend_schema_view(
    get=extend_schema(
        summary="List Comments for a Post",
        responses={200: CommentSerializer(many=True)},
        description="Retrieves a list of comments for a specific post, optionally paginated.",
        tags=['Comments']
    ),
    post=extend_schema(
        summary="Create a Comment for a Post",
        request=CommentSerializer,
        responses={201: CommentSerializer},
        description="Creates a new comment for a specific post.",
        tags=['Comments']
    )
)
@api_view(['GET', 'POST'])
def comments(request, author_id, post_id):
    if Author.objects.filter(pk=author_id).exists() and Post.objects.filter(pk=post_id).exists():
        post_data = Post.objects.get(pk=post_id)

        if request.method == 'GET':            
            comments = Comment.objects.filter(post=post_data).order_by('-published_at')

            page_number = None
            page_size = None
            if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
                page_size = request.GET.get('size')
                page_number = request.GET.get('page')
                paginated = Paginator(comments, page_size)
                comments = paginated.get_page(page_number)

            comments_serialized = CommentSerializer(comments, many=True)

            output = {'type': 'comments', 'page': page_number, 'size': page_size, 'post': post_data.url, 'id': post_data.url + '/comments', 'comments': comments_serialized.data}

            return Response(output, status=status.HTTP_200_OK)
    
        elif request.method == 'POST': 
            author = Author.objects.get(pk=author_id)
            comment_serializer = CommentSerializer(data=request.data)

            if comment_serializer.is_valid():
                comment_serializer.save()
            else:
                return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            comment_obj = Comment.objects.get(author_of_posts=None)
            comment_obj.comment_author = author
            comment_obj.url = post_data.url + '/comments/' + str(comment_obj.comment_id)
            comment_obj.save()

            output = CommentSerializer(comment_obj)
            
            return Response(output.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema_view(
    get=extend_schema(
        summary="List Likes for a Post",
        responses={200: LikeSerializer(many=True)},
        description="Returns all likes for a specified post by a given author, ordered by date.",
        tags=['Likes']
    )
)
@api_view(['GET'])
def posts_likes(request, author_id, post_id):
    if Author.objects.filter(pk=author_id).exists() and Post.objects.filter(pk=post_id).exists():
        author = Author.objects.get(pk=author_id)
        post = Post.objects.get(pk=post_id)

        if request.method == 'GET':
            likes = Like.objects.filter(like_post=post).order_by('-date')
            likes_serialized = LikeSerializer(likes, many=True)
            output = {'type': 'likes', 'items': likes_serialized.data}

            return Response(output, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema_view(
    get=extend_schema(
        summary="List Likes for a Comment",
        responses={200: LikeSerializer(many=True)},
        description="Returns all likes for a specified comment by the comment's ID.",
        tags=['Likes']
    )
)
@api_view(['GET'])
def comments_likes(request, author_id, post_id, comment_id):
    if Comment.objects.filter(pk=comment_id).exists():
        comment = Comment.objects.get(pk=comment_id)

        if request.method == 'GET':
            likes = Like.objects.filter(like_comment=comment).order_by('-date')
            likes_serialized = LikeSerializer(likes, many=True)
            output = {'type': 'likes', 'items': likes_serialized.data}

            return Response(output, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema_view(
    get=extend_schema(
        summary="List Likes by Author",
        responses={200: LikeSerializer(many=True)},
        description="Returns all likes made by a specified author, ordered by date in descending order.",
        tags=['Likes']
    )
)
@api_view(['GET'])
def liked(request, author_id):
    if Author.objects.filter(pk=author_id).exists():
        author = Author.objects.get(pk=author_id)

        if request.method == 'GET':
            likes = Like.objects.filter(author_like=author).order_by('-date')
            likes_serialized = LikeSerializer(likes, many=True)
            output = {'type': 'liked', 'items': likes_serialized.data}

            return Response(output, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Inbox Items",
        responses={200: None},  # Specify a custom serializer or structure if needed
        description="Returns all inbox items (posts, comments, likes, follows) for a specific author.",
        tags=['Inbox']
    ),
    post=extend_schema(
        summary="Add an Item to Inbox",
        request=None,  
        responses={201: None},  
        description="Adds a new item (post, comment, like, follow) to the author's inbox.",
        tags=['Inbox']
    ),
    delete=extend_schema(
        summary="Delete Inbox Item",
        responses={204: None},
        description="Conditionally deletes an item from the author's inbox.",
        tags=['Inbox']
    )
)
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def inbox(request, author_id):
    if Author.objects.filter(pk=author_id).exists():

        print('\n1\n')
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

            if isinstance(request.GET.get('size'), str) and isinstance(request.GET.get('page'), str):
                page_size = request.GET.get('size')
                page_number = request.GET.get('page')
                paginated = Paginator(inbox_list, page_size)
                page = paginated.get_page(page_number)
                inbox_list = page.object_list

            output = {'type': 'inbox', 'author': getattr(author, 'url'), 'items': inbox_list}

            return Response(output, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            print('\n2\n')

            if Node.objects.filter(node_user=request.user).exists():
                node = Node.objects.get(node_user=request.user)
                if not node.approved:
                    return Response({'error': 'Node not approved for posting'}, status=status.HTTP_403_FORBIDDEN)

            
            if request.data.get('type').lower() == 'post':
                print('\n3\n')
                post_auth = request.data.get('author')
                cont_type = request.data.get('contentType')
                post_obj = None

                if not Author.objects.filter(url=post_auth.get('id')).exists():
                    author_serializer = AuthorSerializer(data=post_auth)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                print('\n4\n')    
                if not Post.objects.filter(url=request.data.get('id')).exists():
                    post_serializer = None                                 
                    if cont_type == 'text/plain' or cont_type == 'text/markdown':
                        post_serializer = TextPostSerializer(data=request.data)
                    else:
                        image_post = request.data
                        print(image_post)
                        if image_post.get('content').startswith('data'):
                            str_list = image_post.get('content').split(',', 1)
                            image_post['content'] = str_list[1]
                        post_serializer = ImagePostSerializer(data=request.data)

                    print('\n5\n')
                    if post_serializer.is_valid():
                        post_serializer.save()
                    else:
                        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    print('\n6\n')
                    post_obj = Post.objects.get(url=request.data.get('id'))
                    post_obj.author_of_posts = Author.objects.get(url=post_auth.get('id'))
                    post_obj.save()
                else:
                    print('\n5b\n')
                    post_obj = Post.objects.get(url=request.data.get('id'))              
                
                print('\n7\n')
                author.postInbox.add(post_obj)
                output = None
                if cont_type == 'text/plain' or cont_type == 'text/markdown':
                    output = TextPostSerializer(post_obj)
                else:
                    output = ImagePostSerializer(post_obj)

                print('\n8\n')   
                return Response(output.data, status=status.HTTP_201_CREATED)

            elif request.data.get('type').lower() == 'comment':
                comment_auth = request.data.get('author')
                comment_url = request.data.get('id')
                split_url = comment_url.rsplit('/', 2)
                post_url = split_url[0]
                comment_obj = None
                
                if not Post.objects.filter(url=post_url).exists():
                    return Response({'error': 'Post of comment does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                if not Author.objects.filter(url=comment_auth.get('id')).exists():
                    author_serializer = AuthorSerializer(data=comment_auth)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                if not Comment.objects.filter(url=comment_url).exists():    
                    comment_serializer = CommentSerializer(data=request.data)
                    if comment_serializer.is_valid():
                        comment_serializer.save()
                    else:
                        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    comment_obj = Comment.objects.get(comment_author=None)
                    comment_obj.comment_author = Author.objects.get(url=comment_auth.get('id'))
                    comment_obj.post = Post.objects.get(url=post_url)
                    comment_obj.save()
                else:
                    comment_obj = Comment.objects.get(url=comment_url)
                
                author.commentInbox.add(comment_obj)
                output = CommentSerializer(comment_obj)
                return Response(output.data, status=status.HTTP_201_CREATED)

            elif request.data.get('type').lower() == 'like':
                like_author = request.data.get('author')
                obj_url = request.data.get('object')
                like_obj = None

                if not Post.objects.filter(url=obj_url).exists() and not Comment.objects.filter(url=obj_url).exists():
                    return Response({'error': 'Object of like does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                if not Author.objects.filter(url=like_author.get('id')).exists():
                    author_serializer = AuthorSerializer(data=like_author)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                if not Like.objects.filter(object=obj_url).filter(author_like__url=like_author.get('id')).exists():
                    like_serializer = LikeSerializer(data=request.data)
                    if like_serializer.is_valid():
                        like_serializer.save()
                    else:
                        return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    like_obj = Like.objects.get(author_like=None)
                    like_obj.author_like = Author.objects.get(url=like_author.get('id'))
                    if Post.objects.filter(url=obj_url).exists():
                        post = Post.objects.get(url=obj_url)
                        like_obj.like_post = post
                        post.num_likes += 1
                        post.save()
                    else:
                        like_obj.like_comment = Comment.objects.get(url=obj_url)
                    like_obj.save()
                else:                
                    like_obj = Like.objects.filter(object=obj_url).filter(author_like__url=like_author.get('id')).get()
                
                author.likeInbox.add(like_obj)
                output = LikeSerializer(like_obj)
                return Response(output.data, status=status.HTTP_201_CREATED)

            elif request.data.get('type').lower() == 'follow':
                follow_auth = request.data.get('actor')
                obj_auth = request.data.get('object')
                follow_obj = None

                if not getattr(author, 'url') == obj_auth.get('id'):
                    return Response({'error': 'Improper inbox for object of follow'}, status=status.HTTP_400_BAD_REQUEST)
                
                if not Author.objects.filter(url=follow_auth.get('id')).exists():
                    author_serializer = AuthorSerializer(data=follow_auth)
                    if author_serializer.is_valid():
                        author_serializer.save()
                    else:
                        return Response(author_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                if not Follow.objects.filter(actor__url=follow_auth.get('id')).filter(object_of_follow__url=obj_auth.get('id')).exists():
                    follow_serializer = FollowSerializer(data=request.data)
                    if follow_serializer.is_valid():
                        follow_serializer.save()
                    else:
                        return Response(follow_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    follow_obj = Follow.objects.get(actor=None)
                    follow_obj.actor = Author.objects.get(url=follow_auth.get('id'))
                    follow_obj.object_of_follow = author
                    follow_obj.save()
                else:
                    follow_obj = Follow.objects.filter(actor__url=follow_auth.get('id')).filter(object_of_follow__url=obj_auth.get('id')).get()
                
                author.followInbox.add(follow_obj)
                output = FollowSerializer(follow_obj)
                return Response(output.data, status=status.HTTP_201_CREATED)
            
            else:
                return Response({'error': 'Unrecognized object type'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            author.postInbox.clear()
            author.commentInbox.clear()
            author.likeInbox.clear()
            author.followInbox.clear()

            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    else:
        return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
    
@extend_schema(
    methods=['POST'], 
    summary="Send Friend Request",
    description="Sends a friend request from the authenticated user to another author.",
    request=FollowSerializer,  
    responses={200: 'Your success response structure here', 404: 'Your error response structure here'},  # Specify actual structure
    tags=['Friend Requests'],
    operation_id='send_friend_request',
)
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

                # HTTP Request to POST new follow request to inbox of receipient author
                print(receiver.host)
                print(receiver.url)
                node = Node.objects.get(host_url=receiver.host)
                output = FollowSerializer(friend_request)
                print(output.data)
                print(node.username_out)
                print(node.password_out)
                response = requests.post(receiver.url + '/inbox', json=output.data, auth=HTTPBasicAuth(node.username_out, node.password_out), headers={'Content-Type': 'application/json'})
                print(response.status_code)

                # TODO: If receiver of follow request is foreign, create follower object immediately
                ###########THIS IF STATEMENT WAS ADDED########################
                if not receiver.host == request.build_absolute_uri('/'):
                    if Follower.objects.filter(follower=author, followee=receiver).exists():
                        context['result'] = "You are already following this user"
                        return Response(context, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Create Follower object
                    follower = Follower.objects.create(follower=author, followee=receiver)

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


@extend_schema(
    request=None,  
    responses={201: FollowerSerializer, 400: None, 404: None, 401: None},
    summary="Accept a Friend Request",
    description="Accepts a friend request between two authors, creating a follower relationship.",
    methods=['POST'],
    tags=['Friendships']
)
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
                    # follow_request.active = False
                    follow_request.delete()
                    # follow_request.save()

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

@extend_schema(
    summary="Cancel Follow Request",
    description="Cancels an active follow request between two authors.",
    request=None,  
    responses={
        200: None,  
        404: None,  
        401: None,
    },
    methods=['POST'],
    tags=['Follow Management']
)
@api_view(['POST'])
def cancel_follow_request(request):
    if request.method == "POST" and request.user.is_authenticated:
        user_id = request.POST.get("user_id")
        try:
            object_of_follow = Author.objects.get(pk=user_id)
            actor = Author.objects.get(user=request.user)
            print(actor)
            follow_request = Follow.objects.filter(actor=actor, object_of_follow=object_of_follow, active=True).first()
            print(follow_request)
            follow_request.delete()
            return JsonResponse({'result': 'Successful'})
        except Follow.DoesNotExist:
            return JsonResponse({'result': 'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'result': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    request=None,  
    responses={200: None},  
    summary="Unfollow a User",
    description="Allows an authenticated user to unfollow another user. Requires 'user_id' as POST parameter.",
    methods=['POST'],  
    tags=['Followers'],  
)
@api_view(['POST'])
def unfollow_user(request):
    if request.method == "POST" and request.user.is_authenticated:
        user_id = request.POST.get("user_id")
        try:
            followee = Author.objects.get(pk=user_id)
            follower = Author.objects.get(user=request.user)
            follower_object = Follower.objects.filter(follower=follower, followee=followee).first()
            print(follower_object)
            follower_object.delete()

            return JsonResponse({'result': 'Successful'})
        except Follow.DoesNotExist:
            return JsonResponse({'result': 'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'result': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



def check_inbox(request):
    five_seconds_ago = timezone.now() - timezone.timedelta(seconds=5)
    
    current_time = timezone.now()

    recent_posts = Post.objects.filter(
        published_at__gte=five_seconds_ago,  # Posts made in the last minute
        published_at__lte=current_time,   # Posts made up to the current time
    )
    
    toggle_option = request.GET.get('toggleOption')
    show_friends_posts = toggle_option == 'friends'  

    friend_posts = []
    visible_posts = []
    posts = []
    currentUser_asAuthor = Author.objects.get(user=request.user)
    
    # for admin access 
    
    # check approval if its required by admin
    approval_instance, created = Approval.objects.get_or_create(id=1, defaults={'require_approval': True})
    
    # check if approval is required
    if approval_instance.require_approval:
        if currentUser_asAuthor.is_approved:
            for post in recent_posts:
                if post.visibility == 'PUBLIC':
                    visible_posts.append(post)
                    if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists() or post.author_of_posts == currentUser_asAuthor:
                        friend_posts.append(post)
                # dont add users friends only posts
                elif post.visibility == 'FRIENDS' and post.author_of_posts != currentUser_asAuthor:
                    if Follower.objects.filter(followee=post.author_of_posts, follower=currentUser_asAuthor).exists() or post.author_of_posts == currentUser_asAuthor:
                        if Follower.objects.filter(followee=currentUser_asAuthor, follower=post.author_of_posts) or post.author_of_posts == currentUser_asAuthor:
                            # visible_posts.append(post)
                            friend_posts.append(post)
                elif post.visibility == 'UNLISTED' and request.user.is_authenticated:
                    if post.author_of_posts.user == request.user:
                        visible_posts.append(post)
                        friend_posts.append(post)
            
        
            if toggle_option == 'all':
                posts = visible_posts
                print(posts)
                template_name = 'socialNetworking/replace_post.html'
            else:
                posts = friend_posts
                template_name = 'socialNetworking/replace_post.html'
            
    print(recent_posts)
    context = {
                'post_list': posts,
            }
            
    return render(request, 'socialNetworking/replace_post.html', context)
   