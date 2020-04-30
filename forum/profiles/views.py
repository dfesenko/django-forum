from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.base import View

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import UserInfoForm, ProfileInfoForm
from .models import Profile
from discussions.views import CheckUserMixin
from discussions.models import Post


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'profiles/user_profile.html'


class UserActivityView(generic.ListView):
    template_name = 'profiles/user_forum_activity.html'
    context_object_name = 'user_posts_list'

    def get_queryset(self):
        author = User.objects.get(pk=int(self.kwargs['pk']))
        return Post.objects.filter(author=author).order_by("-creation_date")


class UserPageView(CheckUserMixin, View):
    """
    The view for redirecting user to his/her profile page with dynamic url
    """

    def get(self, request, *args, **kwargs):
        return redirect('profiles:user_details', pk=request.user.pk)


class UserPageEditView(CheckUserMixin, View):

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

        return render(request, 'profiles/profile_edit.html', {'user_form': user_form,
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

            return redirect('profiles:user_details', pk=request.user.pk)
