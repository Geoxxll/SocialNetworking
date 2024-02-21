from django.contrib import admin
from .models.authors import Author
from .models.followers import Follower
from .models.follow import Follow
from .models.posts import Post

# Register your models here.

admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(Follow)
admin.site.register(Post)