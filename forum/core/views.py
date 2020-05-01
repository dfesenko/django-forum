from django.contrib.auth.models import User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class IndexView(generic.ListView):
    template_name = 'core/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        return User.objects.all()


class CheckUserMixin(LoginRequiredMixin):
    login_url = reverse_lazy('registration:login')
