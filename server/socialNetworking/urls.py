from django.urls import path
from .views import CommentDeleteView, PostDeleteView, PostListView, PostDetailView, AddPostView, ProfileView,PostEditView
from . import views

urlpatterns = [
    path('social/', PostListView.as_view(), name='post-list'),
    path('social/post/', AddPostView.as_view(), name='add-post'),
    path('social/profile/', ProfileView.as_view(), name='profile-view'),
    path('social/post/edit/<uuid:pk>/', PostEditView.as_view(), name='post-edit'),
    path('social/post/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),
	path('social/post/delete/<uuid:pk>/', PostDeleteView.as_view(), name='post-delete'),
 	path('social/post/<uuid:post_pk>/comment/delete/<uuid:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    #path("api/authors/", views.authors, name="authors"),
    #path("api/authors/<uuid:author_id>/", views.authors_id, name="authors_id"),
    #path("api/authors/<uuid:author_id>/followers/", views.followers, name="followers"),
    #path("api/authors/<uuid:author_id>/followers/<uuid:foreign_author_id>/", views.followers_id, name="followers_id"),
    #path("api/authors/<uuid:author_id>/posts/", views.posts, name="posts"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/", views.posts_id, name="posts_id"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/image/", views.image, name="image"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/", views.comments, name="comments"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/likes/", views.posts_likes, name="posts_likes"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes/", views.comments_likes, name="comments_likes"),
    #path("api/authors/<uuid:author_id>/liked/", views.liked, name="liked"),
    #path("api/authors/<uuid:author_id>/inbox/", views.inbox, name="inbox"),
]