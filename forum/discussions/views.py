from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import generic

from django.contrib.auth.models import User


def index(request):
    return HttpResponse("Hello, world. You're at the forum's index.")


class DetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'

