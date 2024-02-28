from django.db import models
import uuid

class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    type = models.CharField(max_length=15, default='comment', editable=False)
    comment = models.TextField()
    #TODO: possibly support multiple contentType (image? plain_text)
    contentType = models.CharField(max_length=20, default='text/markdown', editable=False)
    published_at = models.DateTimeField(auto_now_add=True)

    comment_author = models.ForeignKey('Author', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    likes = models.ManyToManyField('Author', blank=True, related_name='comment_likes')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    
    
    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-published_at').all()
    
    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False