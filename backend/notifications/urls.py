from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotifyConfigViewSet, NotifyTemplateViewSet

router = DefaultRouter()
router.register(r'config', NotifyConfigViewSet, basename='notify-config')
router.register(r'templates', NotifyTemplateViewSet, basename='notify-template')

urlpatterns = [
    path('', include(router.urls)),
]


