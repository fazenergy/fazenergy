from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AffiliateViewSet, UserProfileView

router = DefaultRouter()
router.register(r'affiliates', AffiliateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
