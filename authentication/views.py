import _thread as thread

from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.token import account_activation_token
from authentication.permissions import IsNotAuthenticated
from authentication.models import User
from authentication.serializers import UserAuthenticationSerializer, UserProfileSerializer


class UserLogin(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        try:
            response = super(UserLogin, self).post(request, *args, **kwargs)
            if response.status_code == HTTP_200_OK:
                user = User.objects.get(username=request.data["username"])
                user.login_handle()
            return response
        except InvalidToken:
            return Response(status=HTTP_400_BAD_REQUEST)


class UserSignupView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserAuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            thread.start_new_thread(user.send_verification_email, (request, ))

            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, uidb64, token):
        try:
            user = User.objects.get(pk=force_text(urlsafe_base64_decode(uidb64)))
            if account_activation_token.check_token(user, token):
                user.update(is_email_verified=True)
                return Response("thank for your email confirmation. Now you can login your account", status=HTTP_200_OK)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        return Response("Activation link is invalid", status=HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        return Response(status=HTTP_200_OK)


class ViewProfiles(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        if username is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(user)
        data = serializer.data
        if username == request.user.username:
            data.update({"credit": request.user.credit, "ranked_game_lives": request.user.ranked_game_lives})
        return Response(data, status=HTTP_200_OK)
