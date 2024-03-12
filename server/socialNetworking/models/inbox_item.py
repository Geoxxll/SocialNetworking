from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class InboxItem(models.Model):
  type = models.CharField(max_length=15, editable=False, default='inbox item')
  items_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  items_object_id = models.UUIDField()
  items = GenericForeignKey('items_content_type', 'items_object_id')
  
  