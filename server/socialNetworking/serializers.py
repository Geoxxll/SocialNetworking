from rest_framework import serializers
from .models.authors import Author
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        # fields can be reduced later if no need.
        fields = ['user', 'type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

