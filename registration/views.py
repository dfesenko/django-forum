from django.views.generic.base import View

from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetDoneView, PasswordChangeDoneView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.contrib.sites.shortcuts import get_current_site

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.core.exceptions import ObjectDoesNotExist

from django.template.loader import render_to_string

from django.core.mail import send_mail

from .decorators import async_func
from .tokens import account_activation_token

from .forms import SignupForm


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
            return redirect('registration:email_confirm')
        else:
            return render(request, 'registration/signup.html', {'form': form})


class EmailConfirmView(View):
    def get(self, request):
        return render(request, 'registration/email_confirm.html')


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


class UserPasswordResetDoneView(UserPassesTestMixin, PasswordResetDoneView):
    login_url = reverse_lazy('core:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_reset = '/password-reset/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_reset and not self.request.user.is_authenticated
        return allow_access


class UserPasswordChangeDoneView(UserPassesTestMixin, PasswordChangeDoneView):
    login_url = reverse_lazy('core:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_change = '/password-change/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_change and self.request.user.is_authenticated
        return allow_access