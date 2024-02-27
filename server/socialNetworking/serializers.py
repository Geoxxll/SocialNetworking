from rest_framework import serializers
from .models.authors import Author
from .models.followers import Follower
from .models.comments import Comment
from .models.likes import Like

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        # fields can be reduced later if no need.
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        # fields can be reduced later if no need.
        fields = ['type', 'follower', 'followee', 'followed_at']

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='comment_author')
    published = serializers.DateTimeField(source='published_at')
    id = serializers.UUIDField(source='comment_id')

    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType', 'published', 'id']

# class LikeSerializer(serializers.ModelSerializer):
#    author = AuthorSerializer(source='author_like')
#
#    class Meta:
#        model = Like
#        fields = ['context', 'summary', 'type', 'author', 'object']