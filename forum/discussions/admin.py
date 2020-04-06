from django.contrib import admin

from .models import Profile, Message, DeletedMessage, ReadMessages, Category, Topic, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('last_updated_date', 'category_name', 'topics_amount')


admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(DeletedMessage)
admin.site.register(ReadMessages)
