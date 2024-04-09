from rest_framework import serializers
from .models.authors import Author
from .models.followers import Follower
from .models.follow import Follow
from .models.posts import Post
from .models.comments import Comment
from .models.likes import Like
from .models.inbox import Inbox
from .models.inbox_item import InboxItem
import base64

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source='url', read_only=True)

    class Meta:
        model = Author
        # fields can be reduced later if no need.
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        # fields can be reduced later if no need.
        fields = ['type', 'follower', 'followee', 'followed_at']

class FollowSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer(read_only=True)
    object = AuthorSerializer(source='object_of_follow', read_only=True)
    published = serializers.DateTimeField(source='date', read_only=True)

    class Meta:
        model = Follow
        fields = ['type', 'summary', 'actor', 'object', 'published']

class TextPostContentField(serializers.Field):
    def to_representation(self, value):
        return str(value, 'utf-8')
    
    def to_internal_value(self, data):
        return bytes(data, 'utf-8')
    
class TextPostSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source='url')
    author = AuthorSerializer(source='author_of_posts', read_only=True)
    published = serializers.DateTimeField(source='published_at')
    content = TextPostContentField()

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'published', 'visibility']

class ImagePostContentField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    
    def to_internal_value(self, data):
        return base64.b64decode(data)

class ImagePostSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source='url')
    author = AuthorSerializer(source='author_of_posts', read_only=True)
    published = serializers.DateTimeField(source='published_at')
    content = ImagePostContentField()

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'published', 'visibility']

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='comment_author', read_only=True)
    published = serializers.DateTimeField(source='published_at')
    id = serializers.URLField(source='url')

    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType', 'published', 'id']

class LikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='author_like', read_only=True)
    published = serializers.DateTimeField(source='date', read_only=True)

    class Meta:
        model = Like
        fields = ['summary', 'type', 'author', 'object', 'published']


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



    