from django.db import models
import uuid
from django.contrib.auth.models import User

class Post (models.Model):
    contentTypesChoices = {
        'COMMON_MARK':'text/markdown',
        'PLAIN':'text/plain',
        'BASE64':'application/base64',
        'PNG':'image/png;base64',
        'JPEG':'image/jpeg;base64',
    }

    class VisibilityChoices(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        FRIENDS = 'FRIENDS', 'Friends'
        UNLISTED = 'UNLISTED', 'Unlisted'

    shared_body = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=15, default='post', editable=False)
    post_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    source = models.URLField()
    origin = models.URLField()
    description = models.TextField()
    contentType = models.CharField(max_length=30, choices=contentTypesChoices.items(), default='PLAIN')
    content = models.BinaryField(null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC)
    published_at =models.DateTimeField(auto_now_add=True)
    shared_on = models.DateTimeField(blank=True, null=True)
    author_of_posts = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='posts_set')
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    likes = models.ManyToManyField('Author', blank=True, related_name='likes')

    class Meta:
        ordering = ['-published_at', '-shared_on']

    def __str__(self) -> str:
        return "title: {}, type: {}, source: {}, origin: {}, description: {}, contentType: {}, visibility: {}, published_at: {}".format(
            self.title,
            self.type,
            self.source,
            self.origin,
            self.description,
            self.contentType,
            self.visibility,
            self.published_at
        )

