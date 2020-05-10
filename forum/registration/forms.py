from django.forms import EmailField
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duplicate_email(user_email):
    if user_email in User.objects.all().values_list('email', flat=True):
        raise ValidationError(
            _('%(email)s is already used by another registered user. Choose another email.'),
            params={'email': user_email},
        )


class SignupForm(UserCreationForm):
    email = EmailField(max_length=200, help_text='Required', required=True, validators=[validate_duplicate_email])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')