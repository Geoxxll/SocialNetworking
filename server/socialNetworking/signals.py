from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models.authors import Author
from .uriConstructor import construct_default_author_uri

@receiver(user_signed_up)
def create_author_for_user(sender, request, user, **kwargs):
    host =  f"{request.build_absolute_uri('/')}"
    author = Author.objects.create(
        user=user,
        displayName=user.username,
        host = host,
    )
    author.url = construct_default_author_uri(author, request, host)
    author.save()
    




    