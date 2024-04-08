from django.contrib import admin
from .models.authors import Author
from .models.followers import Follower
from .models.follow import Follow
from .models.posts import Post
from .models.comments import Comment
from .models.likes import Like
from .models.inbox import Inbox
from .models.inbox_item import InboxItem
from .models.nodes import Node
from .models.approval import Approval
# Register your models here.

admin.site.register(Node)
admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Inbox)
admin.site.register(InboxItem)
admin.site.register(Approval)