from django.forms import EmailField
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    email = EmailField(max_length=200, help_text='Required', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')