from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.base import View

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from .forms import UserInfoForm


class IndexView(generic.ListView):
    template_name = 'discussions/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        """Return list of registered users"""
        return User.objects.all()


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'


class UserPageView(View):
    """
    The view for redirecting user to his/her profile page with dynamic url
    """
    login_url = reverse_lazy('discussions:login')

    def test_func(self):
        allow_access = self.request.user.is_authenticated
        return allow_access

    def get(self, request, *args, **kwargs):
        return redirect(f'/users/{request.user.pk}/')


class UserSignupView(View):
    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

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


class UserPageEditView(UserPassesTestMixin, View):
    login_url = reverse_lazy('discussions:login')

    def test_func(self):
        allow_access = self.request.user.is_authenticated
        return allow_access

    def get(self, request, *args, **kwargs):
        user_form = UserInfoForm()
        return render(request, 'discussions/profile_edit.html', {'user_form': user_form})

    def post(self, request, *args, **kwargs):
        user_instance = get_object_or_404(User, id=request.user.pk)
        user_form = UserInfoForm(request.POST, instance=user_instance)
        if user_form.is_valid():
            not_empty_fields = [k for k, v in user_form.cleaned_data.items() if v]
            model_instance = user_form.save(commit=False)
            model_instance.save(update_fields=not_empty_fields)
            return redirect(f'/users/{request.user.pk}/')


class UserPasswordResetDoneView(UserPassesTestMixin, PasswordResetDoneView):
    login_url = reverse_lazy('discussions:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_reset = '/password_reset/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_reset and not self.request.user.is_authenticated
        return allow_access






