from django.contrib.auth.models import User
from django.test import TestCase

from accounts import views
from accounts.tokens import account_activation_token


class UserAuthTestCase(TestCase):
    def test_create_user_and_send_email(self):
        # create dummy form response
        views.signup_view()
        self.assertTrue()


class TokensTestCase(TestCase):
    def test_token_generation(self):
        user = User.objects.create(username='test')
        token = account_activation_token.make_token(user)
        self.assertTrue(account_activation_token.check_token(user, token))
