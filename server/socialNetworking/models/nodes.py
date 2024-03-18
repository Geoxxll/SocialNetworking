from django.db import models

class Node (models.Model):
    host_url = models.URLField(primary_key=True)
    api_url = models.URLField()
    username_in = models.CharField(max_length=20)
    password_in = models.CharField(max_length=20)
    username_out = models.CharField(max_length=20)
    password_out = models.CharField(max_length=20)
    approved = models.BooleanField(default=True)

    def __str__ (self):
        return f"{self.host_url} - Approved: {self.approved}"