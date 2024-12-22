from django.contrib import admin
from blog.models.models import *
from blog.models.posts import Post
from blog.models.models import Writer




# Register your models here.


#admin.site.register(Post, PostAdmin) # by declaring this, Post model is used in admin panel by my custom view PostAdmin
admin.site.register(Writer)
admin.site.register(Article)
admin.site.register(Post)