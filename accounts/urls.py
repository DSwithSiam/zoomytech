from django.urls import path
from .views import *

urlpatterns = [
   path('signup/', signup, name='signup'),
   path('resend-otp/', resend_otp, name='resend_otp'),
   path('activate/', activate, name='activate'),
   path('login/', login, name='login'),
   path('token/refresh/', custom_token_refresh, name='custom_token_refresh'),
   path('logout/', logout, name='logout'),
   path('profile/', profile, name='profile'),
   path('password-reset-request/', pass_reset_request, name='pass_reset_request'),
   path('reset-request-activate/', reset_request_activate, name='reset_request_activate'),
   path('reset-password/', reset_password, name='reset_password'),
   path('delete-user/', delete_user, name='delete_user'),
]