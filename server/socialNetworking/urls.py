from django.urls import path
from .views import PostListView, PostDetailView


urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),

]