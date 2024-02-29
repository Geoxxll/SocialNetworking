from django.urls import path
from .views import (
  SharedPostView, 
  CommentReplyView,  
  AddCommentLike, 
  AddLike, 
  DashboardView, 
  CommentDeleteView, 
  PostDeleteView, 
  PostListView, 
  PostDetailView, 
  AddPostView, 
  ProfileEditView,
  PostEditView,
  FindFriendsView, 
  send_friend_request,
  accept_friend_request,
  InboxView,
  )
from . import views

urlpatterns = [
    # serializer test url
    # path('serializer/authors/', views.authors, name='authors'),
    # path('serializer/authors/<uuid:author_id>/', views.authors_id, name='authorId'),
    # path('serializer/followers/<uuid:author_id>/', views.followers, name='followers'),
    # path('serializer/followers/<uuid:author_id>/<uuid:foreign_author_id>/', views.followers_id, name='followersId'),

	
    path('social/', PostListView.as_view(), name='post-list'),
    path('social/accept-request', accept_friend_request, name='accept-friend-request'),
    path('social/post/', AddPostView.as_view(), name='add-post'),
    path('social/find-friends/', FindFriendsView.as_view(), name='find-friends'),
    path('social/find-friends/send-request', send_friend_request, name='send-friend-request'),

    path('social/profile/', DashboardView.as_view(), name='profile'),
    path('social/post/edit/<uuid:pk>/', PostEditView.as_view(), name='post-edit'),
    path('social/post/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),
	  path('social/post/delete/<uuid:pk>/', PostDeleteView.as_view(), name='post-delete'),
 	  path('social/post/<uuid:post_pk>/comment/delete/<uuid:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('social/profile/edit/<uuid:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('social/post/<uuid:pk>/like', AddLike.as_view(), name='like'),
    path('social/post/<uuid:post_pk>/comment/<uuid:pk>/like', AddCommentLike.as_view(), name='comment-like'),
    path('social/post/<uuid:post_pk>/comment/<uuid:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('social/post/<uuid:pk>/share', SharedPostView.as_view(), name='share-post'),

    path("api/authors/", views.authors, name="authors"),
    path("api/authors/<uuid:author_id>/", views.authors_id, name="authors_id"),
    path("api/authors/<uuid:author_id>/followers/", views.followers, name="followers"),
    #path("api/authors/<uuid:author_id>/followers/<uuid:foreign_author_id>/", views.followers_id, name="followers_id"),
    path("api/authors/<uuid:author_id>/posts/", views.posts, name="posts"),
    path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/", views.posts_id, name="posts_id"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/image/", views.image, name="image"),
    path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/", views.comments, name="comments"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/likes/", views.posts_likes, name="posts_likes"),
    #path("api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes/", views.comments_likes, name="comments_likes"),
    #path("api/authors/<uuid:author_id>/liked/", views.liked, name="liked"),
    path("api/authors/<uuid:author_id>/inbox/", InboxView.as_view(), name="get_inbox"),
    path("api/authors/<uuid:author_id>/inbox/<uuid:item_id>", InboxView.as_view(), name="post_into_inbox"),
]