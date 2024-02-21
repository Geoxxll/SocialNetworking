from django.db import models


class Like(models.Model):
    context = models.URLField(default='https://www.w3.org/ns/activitystreams', editable=False)
    type = models.CharField(max_length=15, default='like', editable=False)
    summary = models.TextField(blank=True)

    author_like = models.ForeignKey('Author', on_delete=models.CASCADE)
    like_post = models.ForeignKey('Post', on_delete=models.CASCADE, null=False, blank=False)
    like_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        '''
            automatically generate like summary
        '''
        if not self.summary:
            self.summary = f"{self.author_like.displayName} likes your post"
        super().save(*args, **kwargs)
