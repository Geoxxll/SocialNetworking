from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .inbox_item import InboxItem

class Inbox(models.Model):
    type = models.CharField(max_length=15, editable=False, default='inbox')
    inbox_owner = models.ForeignKey('Author', on_delete=models.CASCADE)
    item = models.ManyToManyField(InboxItem, related_name='inbox')
    def __str__(self):
        return f"{self.inbox_owner.user.username} 's inbox."
