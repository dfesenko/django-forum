from django.contrib import admin

from .models import Profile, Category, Topic, Post


admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Topic)
admin.site.register(Post)