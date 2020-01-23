import json

from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from authentication.models import User


class AuthenticationTest(TestCase):
    CLIENT_USERNAME = 'test'
    CLIENT_PASSWORD = 'test'

    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username=self.CLIENT_USERNAME,
            password=self.CLIENT_PASSWORD
        )
        self.client.login(
            username=self.CLIENT_USERNAME,
            password=self.CLIENT_PASSWORD
        )
        return super().setUp()

    def test_authentication_token(self):
        response = self.client.post(path="http://localhost:8000/api/login/", data={
            "username": self.CLIENT_USERNAME,
            "password": self.CLIENT_PASSWORD
        }, content_type="application/json")
        self.assertEquals(200, response.status_code)


class ProfileViewTest(TestCase):
    CLIENT_USERNAME = 'user'
    CLIENT_PASSWORD = 'pass'
    CLIENT_FIRST_NAME = 'first'
    CLIENT_LAST_NAME = 'last'

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username=ProfileViewTest.CLIENT_USERNAME,
            password=ProfileViewTest.CLIENT_PASSWORD,
            first_name=ProfileViewTest.CLIENT_FIRST_NAME,
            last_name=ProfileViewTest.CLIENT_LAST_NAME
        )
        self.client.login(
            username=ProfileViewTest.CLIENT_USERNAME,
            password=ProfileViewTest.CLIENT_PASSWORD
        )

        self.access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.access_token))
        return super().setUp()

    def test_profile_view(self):
        response = self.client.get(path="http://localhost:8000/api/profile/", data={
            "username": ProfileViewTest.CLIENT_USERNAME,
        }, content_type="application/json")
        self.assertEquals(200, response.status_code)

        profile = json.loads(response.content)
        self.assertEqual(profile['username'], ProfileViewTest.CLIENT_USERNAME)
        self.assertEqual(profile['first_name'], ProfileViewTest.CLIENT_FIRST_NAME)
        self.assertEqual(profile['last_name'], ProfileViewTest.CLIENT_LAST_NAME)
