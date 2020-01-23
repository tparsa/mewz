from django.contrib.auth.models import AbstractUser, update_last_login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import models
from django.conf import settings
from django.core.mail import send_mail

from authentication.token import account_activation_token


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)

    def login_handle(self):
        update_last_login(None, self)

    def send_verification_email(self, request):
        current_site = get_current_site(request)
        mail_subject = 'Activate your mafia account'
        message = render_to_string('acc_active_email.html', {
            'user': self,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': account_activation_token.make_token(self),
        })

        email_from = settings.EMAIL_HOST_USER
        recipient_list = [self.email, ]

        send_mail(mail_subject, message, email_from, recipient_list)
