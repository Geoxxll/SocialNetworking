from django.db import models
import uuid

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



    title = models.CharField(max_length=100)
    type = models.CharField(max_length=15, default='post', editable=False)
    post_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    source = models.URLField()
    origin = models.URLField()
    description = models.TextField()
    contentTpye = models.CharField(max_length=30, choices=contentTypesChoices, default='PLAIN')
    content = models.BinaryField(null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC)
    published_at =models.DateTimeField(auto_now_add=True)
    author_of_posts = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='posts_set')


