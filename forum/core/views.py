from django.contrib.auth.models import User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class IndexView(generic.ListView):
    template_name = 'core/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['page_title'] = 'Forum website'
        return context


class CheckUserMixin(LoginRequiredMixin):
    login_url = reverse_lazy('registration:login')
