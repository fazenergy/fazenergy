from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProspectViewSet, ProposalViewSet, ProposalResultViewSet

router = DefaultRouter()
router.register(r'prospects', ProspectViewSet)
router.register(r'proposals', ProposalViewSet)
router.register(r'proposal-results', ProposalResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
