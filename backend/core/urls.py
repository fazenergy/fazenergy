from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LicensedViewSet, UserProfileView, validate_referrer, LicensedPreRegisterView

router = DefaultRouter()
router.register(r'licensed', LicensedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('validate-referrer/<str:username>/', validate_referrer, name='validate-referrer'),
    path('pre-register/', LicensedPreRegisterView.as_view(), name='pre-register'),
]