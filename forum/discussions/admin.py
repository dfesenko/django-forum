from django.contrib import admin

from .models import Profile, Message, DeletedMessage


admin.site.register(Profile)
# admin.site.register(Category)
# admin.site.register(Topic)
# admin.site.register(Post)
admin.site.register(Message)
admin.site.register(DeletedMessage)