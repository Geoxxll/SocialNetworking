from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

# Create your views here.
from django.views import View
from .models.posts import Post
from .models.comments import Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from .models.authors import Author
from django.contrib.auth.models import User


class AddPostView(View):
    def get(self, request, *args, **kwargs):
        # posts = Post.objects.all().order_by('-published_at')
        form = PostForm()

        context = {
            
            'form': form,
        }

        # return render(request, 'socialNetworking/post_list.html', context)
        return render(request, 'socialNetworking/post_list.html', context)
    
    def post(self, request, *args, **kwargs):
        
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
            
        posts = Post.objects.all().order_by('-published_at')
        context = {
            'post_list': posts,
            'form': form,
        }

        return render(request, 'socialNetworking/dashboard.html', context)

class PostListView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-published_at')
        form = PostForm()
        
        post_comments = {}
        for post in posts:
            comments = Comment.objects.filter(post=post)
            post_comments[post.post_id] = comments
            
        # print(post_comments)
        context = {
            'post_list': posts,
            'form': form,
            'post_comments': post_comments,
        }

        return render(request, 'socialNetworking/dashboard.html', context)
    
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

        
        comments = Comment.objects.filter(post=post).order_by('-published_at')
        
        
        print("HERE",comments)
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        

        return render(request, 'socialNetworking/post_detail.html', context)


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.filter(author_of_posts__user=request.user).order_by('-published_at')
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
        }

        return render(request, 'socialNetworking/profile_view.html', context)
    
class PostEditView(UpdateView):
    model = Post
    fields = ['description',"visibility"]
    template_name = 'socialNetworking/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile-view')
    
    # def test_func(self):
    #     post = self.get_object()
    #     return self.request.user == post.author_of_posts
    
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'socialNetworking/post_delete.html'
    success_url = reverse_lazy('post-list')

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