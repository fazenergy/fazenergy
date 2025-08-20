from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GatewayConfigViewSet, TransactionViewSet, PaymentLinkViewSet, PaymentLinkLatestView

router = DefaultRouter()
router.register(r'gateway-config', GatewayConfigViewSet, basename='gateway-config')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')

urlpatterns = [
    # Coloque caminhos específicos ANTES do include(router) para não conflitar com detail routes
    path('payment-links/latest/', PaymentLinkLatestView.as_view(), name='payment-link-latest'),
    path('', include(router.urls)),
]


