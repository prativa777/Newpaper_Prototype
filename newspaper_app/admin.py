from django.contrib import admin
from newspaper_app.models import Category, Post, Tag, Contact, UserProfile, Comment, Newsletter
# Register your models here.


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Contact)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Newsletter)