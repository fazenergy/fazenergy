from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LicensedViewSet,
    UserProfileView,
    validate_referrer,
    LicensedPreRegisterView,
    DirectLicensedListView,
    DownlineTreeListView,
)

router = DefaultRouter()
router.register(r'licensed', LicensedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('validate-referrer/<str:username>/', validate_referrer, name='validate-referrer'),
    path('pre-register/', LicensedPreRegisterView.as_view(), name='pre-register'),
    path('directs/', DirectLicensedListView.as_view(), name='licensed-directs'),
    path('downlines/', DownlineTreeListView.as_view(), name='licensed-downlines'),
]