from django.db import models

class Follow(models.Model):
    '''
        actor: there act as the follower
        object_of_follow: people who recive the follow request
    '''
    actor = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='actor_follow_set')
    object_of_follow = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='object_of_follow_set')

    def __str__(self):
        return f'{self.actor.displayName} want to follow {self.object_of_follow.displayName}'