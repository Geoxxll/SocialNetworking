from django.db import models

class Follow(models.Model):
    '''
        actor: there act as the follower
        object_of_follow: people who recive the follow request
    '''
    type = models.CharField(max_length=15, default='follow', editable=False)
    summary = models.TextField(blank=True)
    actor = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='actor_follow_set')
    object_of_follow = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='object_of_follow_set')
    active = models.BooleanField(default=True)


    def __str__(self):
        return f'{self.actor.displayName} want to follow {self.object_of_follow.displayName}'
    
    def save(self, *args, **kwargs):
        '''
            automatically generate follow summary
        '''
        if not self.summary:
            self.summary = f'{self.actor.displayName} want to follow {self.object_of_follow.displayName}'
        super().save(*args, **kwargs)