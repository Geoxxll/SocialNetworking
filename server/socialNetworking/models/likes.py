from django.db import models


class Like(models.Model):
    type = models.CharField(max_length=15, default='like', editable=False)
    summary = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    author_like = models.ForeignKey('Author', on_delete=models.CASCADE, related_name = "user_likes")
    like_post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=False, related_name = "post_likes")
    like_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)

    object = models.URLField(null=True)

    def save(self, *args, **kwargs):
        '''
            automatically generate like summary
        '''
        if not self.summary:
            self.summary = f"{self.author_like.displayName} likes your post"
        super().save(*args, **kwargs)
