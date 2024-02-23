from django.urls import path
from .views import PostListView, PostDetailView


urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    # path('post/', PostListView.as_view(), name='add-post'),
    path('post/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),

]