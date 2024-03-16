from django.db import models
import uuid
from django.contrib.auth.models import User

from .posts import Post
from .comments import Comment
from .likes import Like
from .follow import Follow
# Create your models here.

class Author(models.Model):
    type = models.CharField(max_length=15, default='author', editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    url = models.URLField()
    host = models.URLField()
    displayName = models.CharField(max_length=100)
    github = models.URLField(null=True, blank=True)
    # TODO: url for default profileImage
    profileImage = models.URLField(null=True, blank=True)
    lastCommitFetch = models.DateTimeField(null=True, blank=True, editable=True)

    postInbox = models.ManyToManyField(Post, blank=True)
    commentInbox = models.ManyToManyField(Comment, blank=True)
    likeInbox = models.ManyToManyField(Like, blank=True)
    followInbox = models.ManyToManyField(Follow, blank=True)
    
    # field for admin access
    is_approved = models.BooleanField(default=False, editable=True)

    def __str__(self):
        return self.displayName + f": {self.lastCommitFetch}"
    