from django.contrib import admin
from .models.authors import Author
from .models.followers import Follower
from .models.follow import Follow
from .models.posts import Post
from .models.comments import Comment

# Register your models here.

admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)