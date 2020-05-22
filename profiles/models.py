from django.db import models
from django.contrib.auth.models import User
from discussions.models import Post


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<username>/<filename>
    return '{0}/{1}'.format(instance.user.username, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_location = models.CharField(max_length=30, blank=True)
    user_about = models.TextField(max_length=500, blank=True)
    user_avatar = models.ImageField(upload_to=user_directory_path, blank=True, default='/default.png')

    def __str__(self):
        return self.user.get_full_name()

    def user_posts_amount(self):
        return len(Post.objects.filter(author=self.user))

    def user_last_forum_activity_date(self):
        posts = Post.objects.filter(author=self.user)
        if len(posts) > 0:
            return posts.order_by('-creation_date')[0].creation_date
        else:
            return "-"
