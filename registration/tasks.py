import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .tokens import account_activation_token

from forum.celery import app


@app.task
def send_verification_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
        mail_subject = "Activate your forum's account."
        from_email = 'forum.djangotest@gmail.com'
        to_email = user.email

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        domain = 'localhost:8000'

        html_message = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
        })

        text_message = render_to_string('registration/account_activation_email.txt', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
        })

        send_mail(subject=mail_subject, message=text_message, html_message=html_message,
                  from_email=from_email, recipient_list=[to_email], fail_silently=False)

    except ObjectDoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
