from django.contrib import admin

from .models import Message, DeletedMessage, ReadMessages

admin.site.register(Message)
admin.site.register(DeletedMessage)
admin.site.register(ReadMessages)
