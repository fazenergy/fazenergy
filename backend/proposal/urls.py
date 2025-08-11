# proposal/urls.py
from django.urls import path
from proposal.views.auth import RevoTokenView

urlpatterns = [
    path('token', RevoTokenView.as_view(), name='revo-token'),
]