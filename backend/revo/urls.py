from django.urls import path
from revo.api import auth

urlpatterns = [
    path('token/', auth.TestTokenView.as_view(), name='test_token'),
]
