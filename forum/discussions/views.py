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

from .forms import UserInfoForm, ProfileInfoForm
from .models import Profile


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
        user_instance = get_object_or_404(User, id=request.user.pk)
        initial_user_values = {'first_name': user_instance.first_name,
                               'last_name': user_instance.last_name,
                               'email': user_instance.email}

        profile_instance = get_object_or_404(Profile, user=request.user.pk)
        initial_profile_values = {'user_location': profile_instance.user_location,
                                  'user_about': profile_instance.user_about}

        user_avatar = profile_instance.user_avatar

        user_form = UserInfoForm(initial=initial_user_values)
        profile_form = ProfileInfoForm(initial=initial_profile_values)

        return render(request, 'discussions/profile_edit.html', {'user_form': user_form,
                                                                 'profile_form': profile_form,
                                                                 'user_avatar': user_avatar})

    def post(self, request, *args, **kwargs):
        user_instance = get_object_or_404(User, id=request.user.pk)
        profile_instance = get_object_or_404(Profile, user=request.user.pk)

        user_form = UserInfoForm(request.POST, instance=user_instance)
        profile_form = ProfileInfoForm(request.POST, request.FILES, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            not_empty_fields_user = [k for k, v in user_form.cleaned_data.items() if v]
            user_model_instance = user_form.save(commit=False)
            user_model_instance.save(update_fields=not_empty_fields_user)

            not_empty_fields_profile = [k for k, v in profile_form.cleaned_data.items() if v]
            profile_model_instance = profile_form.save(commit=False)
            profile_model_instance.save(update_fields=not_empty_fields_profile)

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
