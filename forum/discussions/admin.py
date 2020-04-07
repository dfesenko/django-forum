from django.contrib import admin

from .models import Profile, Message, DeletedMessage, ReadMessages, Category, Topic, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'last_updated_date', 'topics_amount')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_title', 'category', 'posts_amount', 'last_updated_date', 'last_active_user')


admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(DeletedMessage)
admin.site.register(ReadMessages)
