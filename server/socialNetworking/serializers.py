from rest_framework import serializers
from .models.authors import Author
from .models.followers import Follower
from .models.posts import Post
from .models.comments import Comment
from .models.likes import Like
from .models.inbox import Inbox
from .models.inbox_item import InboxItem

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

class TextPostContentField(serializers.Field):
    def to_representation(self, value):
        return str(value, 'utf-8')
    
    def to_internal_value(self, data):
        return bytes(data, 'utf-8')
    
class TextPostSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source='url', read_only=True)
    author = AuthorSerializer(source='author_of_posts', read_only=True)
    published = serializers.DateTimeField(source='published_at')
    content = TextPostContentField()

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'published', 'visibility']


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='comment_author', read_only=True)
    published = serializers.DateTimeField(source='published_at')
    id = serializers.UUIDField(source='comment_id', read_only=True)

    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType', 'published', 'id']

# class LikeSerializer(serializers.ModelSerializer):
#    author = AuthorSerializer(source='author_like')
#
#    class Meta:
#        model = Like
#        fields = ['context', 'summary', 'type', 'author', 'object']


class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = '__all__'

    def to_representation(self, obj):
        if isinstance(obj.items, Post):
            return TextPostSerializer(obj.items).data
        elif isinstance(obj.items, Comment):
            return CommentSerializer(obj.items).data

class InboxSerializer(serializers.ModelSerializer):
    item = InboxItemSerializer(many=True, read_only=True)
    class Meta:
        model = Inbox
        fields = ['type', 'inbox_owner', 'item']



    