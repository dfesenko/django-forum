from django.contrib import admin

from .models import Profile, Category, Topic, Post


# class ProfileInline(admin.StackedInline):
#     model = Profile
#     extra = 3
#
#
# class UserAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None,               {'fields': ['question_text']}),
#         ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
#     ]
#     inlines = [ProfileInline]

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Topic)
admin.site.register(Post)