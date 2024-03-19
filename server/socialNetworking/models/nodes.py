from django.db import models
from django.contrib.auth.models import User

class Node (models.Model):
    node_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    host_url = models.URLField(primary_key=True)
    api_url = models.URLField()
    username_out = models.CharField(max_length=20)
    password_out = models.CharField(max_length=20)
    approved = models.BooleanField(default=True)

    def __str__ (self):
        return f"{self.host_url}"