from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.

class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    host = models.URLField()
    displayName = models.CharField(max_length=100)
    github = models.URLField()
    profileImage = models.URLField()

    def __str__(self):
        return self.displayName
    