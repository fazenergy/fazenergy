from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractorViewSet, ProposalViewSet, ProposalResultViewSet
from .revo import RevoAuthView, RevoCEPView, RevoSimulationView

router = DefaultRouter()
router.register(r'contractors', ContractorViewSet)
router.register(r'proposals', ProposalViewSet)
router.register(r'proposal-results', ProposalResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('revo/auth/', RevoAuthView.as_view()),
    path('revo/cep/<str:zipcode>/', RevoCEPView.as_view()),
    path('revo/cep/<str:zipcode>/<str:propertyType>/', RevoCEPView.as_view()),
    path('revo/simulation/', RevoSimulationView.as_view()),
]


