from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.base import View

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetDoneView, PasswordChangeDoneView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.contrib.sites.shortcuts import get_current_site

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token

from django.core.exceptions import ObjectDoesNotExist

from django.template.loader import render_to_string
from django.core.mail import BadHeaderError, send_mail
from .decorators import async_func

from .forms import UserInfoForm, ProfileInfoForm, SignupForm
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

    @async_func
    def send_async_mail(self, subject, text_message, html_message, from_email, to_email):
        send_mail(subject=subject, message=text_message, html_message=html_message,
                  from_email=from_email, recipient_list=[to_email])

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activate your forum's account."
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            html_message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            text_message = render_to_string('registration/account_activation_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            from_email = 'forum.djangotest@gmail.com'
            to_email = form.cleaned_data.get('email')

            self.send_async_mail(subject=mail_subject, text_message=text_message, html_message=html_message,
                                 from_email=from_email, to_email=to_email)

            return render(request, 'registration/email_confirm.html')

        else:
            return render(request, 'registration/signup.html', {'form': form})


class UserActivationView(View):

    def get(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return render(request, 'registration/email_confirm_done.html')
        else:
            return render(request, 'registration/email_confirm_invalid.html')


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


class UserPasswordChangeDoneView(UserPassesTestMixin, PasswordChangeDoneView):
    login_url = reverse_lazy('discussions:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_change = '/password_change/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_change and self.request.user.is_authenticated
        return allow_access
