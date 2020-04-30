from django.contrib.auth.models import User
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'core/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        return User.objects.all()
