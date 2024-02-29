from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
class Inbox(models.Model):
    type = models.CharField(max_length=15, editable=False, default='inbox')
    inbox_owner = models.ForeignKey('Author', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.inbox_owner.user.username} 's inbox."
