from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views import View
from .models.posts import Post
from .forms import PostForm, CommentForm

from .models.authors import Author
from django.contrib.auth.models import User



class PostListView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-published_at')
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
        }

        # return render(request, 'socialNetworking/post_list.html', context)
        return render(request, 'socialNetworking/dashboard.html', context)

    def post(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-published_at')
        form = PostForm(request.POST)

        if form.is_valid():
             # Retrieve the User instance associated with the request
            user_instance = request.user if isinstance(request.user, User) else User.objects.get(username=request.user)

            # Retrieve or create Author instance associated with the User
            author_instance, created = Author.objects.get_or_create(user=user_instance)
            new_post = form.save(commit=False)
            new_post.author_of_posts = author_instance
            new_post.save()
            
            # Create a new, empty form after successfully saving the post
            form = PostForm()
        

        context = {
            'post_list': posts,
            'form': form,
        }

        return render(request, 'socialNetworking/post_list.html', context)
    
class PostDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        # post = get_object_or_404(Post, pk=pk)
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        context = {
            'post': post,
            'form': form,
        }

        return render(request, 'socialNetworking/post_detail.html', context)

    def post(self, request, *args, **kwargs):
        pass