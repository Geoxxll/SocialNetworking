from django.urls import path
from .views import CommentDeleteView, PostDeleteView, PostListView, PostDetailView, AddPostView, ProfileView,PostEditView


urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/', AddPostView.as_view(), name='add-post'),
    path('profile/', ProfileView.as_view(), name='profile-view'),
    path('post/edit/<uuid:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),
	path('post/delete/<uuid:pk>/', PostDeleteView.as_view(), name='post-delete'),
 	path('post/<uuid:post_pk>/comment/delete/<uuid:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]