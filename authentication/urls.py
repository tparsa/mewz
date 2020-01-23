from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from authentication.views import UserSignupView, UserLogout, UserLogin, ViewProfiles


urlpatterns = [
    path('login/', UserLogin.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile/', ViewProfiles.as_view(), name='view_profile'),
    path('activate/<str:uidb64>/<str:token>', UserSignupView.as_view(), name='activate'),
]
