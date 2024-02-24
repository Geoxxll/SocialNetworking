from rest_framework import serializers
from .models.authors import Author
from .models.followers import Follower
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        # fields can be reduced later if no need.
        fields = ['user', 'type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        # fields can be reduced later if no need.
        fields = ['type', 'follower', 'followee', 'followed_at']
