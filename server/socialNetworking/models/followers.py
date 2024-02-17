from django.db import models
from . import authors

class followers:
    follower = models.ForeignKey(authors, related_name='follower_set', on_delete=models.CASCADE)
    followee = models.ForeignKey(authors, related_name='followee_set', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    '''
        Ensure that each follower can only follow the same followee once.
    '''
    class Meta:
        unique_together = ('follower', 'followee')

    def __str__ (self):
        return f'{self.follower.displayName} follows {self.followee.displayName}'
