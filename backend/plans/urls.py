# plans/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PlanViewSet
from .views import PlanViewSet, PlanAdesionViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'plan-adesions', PlanAdesionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]