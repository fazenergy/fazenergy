from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractConfigViewSet, ContractTemplateViewSet

router = DefaultRouter()
router.register(r'config', ContractConfigViewSet, basename='contract-config')
router.register(r'templates', ContractTemplateViewSet, basename='contract-template')

urlpatterns = [
    path('', include(router.urls)),
]


