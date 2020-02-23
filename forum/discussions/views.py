from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import generic

from django.contrib.auth.models import User


class IndexView(generic.ListView):
    template_name = 'discussions/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        """Return list of registered users"""
        return User.objects.all()


class DetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'

