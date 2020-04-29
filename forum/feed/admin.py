from django.contrib import admin

from .models import Subscription, ReadPost


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'creation_date')


admin.site.register(ReadPost)
admin.site.register(Subscription, SubscriptionAdmin)
