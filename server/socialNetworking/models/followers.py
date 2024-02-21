from django.db import models

class Follower(models.Model):
    type = models.CharField(max_length=15, default='follower', editable=False)
    follower = models.ForeignKey('Author', related_name='follower_set', on_delete=models.CASCADE)
    followee = models.ForeignKey('Author', related_name='followee_set', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        '''
            Ensure that each follower can only follow the same followee once.
        '''
        unique_together = ('follower', 'followee')

    def __str__ (self):
        return f'{self.follower.displayName} follows {self.followee.displayName}'
