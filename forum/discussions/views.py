from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.base import View
from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse


class IndexView(generic.ListView):
    template_name = 'discussions/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        """Return list of registered users"""
        return User.objects.all()


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'


class UserSignupView(View):
    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, 'discussions/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            created_user_id = user.pk
            return redirect(f'/users/{created_user_id}/')


class UserLoginView(LoginView):
    template_name = 'discussions/login.html'
    redirect_field_name = 'detail'


class UserPageView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = request.user
            current_user_id = current_user.pk
            return redirect(f'/users/{current_user_id}/')
        else:
            return HttpResponseRedirect(reverse('discussions:login'))
