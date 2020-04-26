from django.contrib import admin

from .models import Profile, Message, DeletedMessage, ReadMessages, Category, Topic, Post, \
                    PostVotes, Subscription, ReadPost


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'last_updated_date', 'topics_amount')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_title', 'category', 'posts_amount', 'last_updated_date', 'last_active_user')


class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'topic', 'votes', 'author')


class PostVotesAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'vote_value')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'creation_date')


admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ReadPost)
admin.site.register(Message)
admin.site.register(DeletedMessage)
admin.site.register(ReadMessages)
admin.site.register(PostVotes, PostVotesAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
