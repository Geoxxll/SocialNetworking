from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.

class Author(models.Model):
    type = models.CharField(max_length=15, default='author', editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    host = models.URLField()
    displayName = models.CharField(max_length=100)
    github = models.URLField(null=True, blank=True)
    # TODO: url for default profileImage
    profileImage = models.URLField(null=True, blank=True)
    lastCommitFetch = models.DateTimeField(null=True, blank=True, editable=True)

    def __str__(self):
        return self.displayName + f": {self.lastCommitFetch}"
    