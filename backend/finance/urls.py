from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GatewayConfigViewSet, TransactionViewSet, PaymentLinkViewSet, PaymentLinkLatestView, VirtualAccountBalanceView,
    BankAccountViewSet, WithdrawRequestViewSet, PixConfigViewSet
)

router = DefaultRouter()
router.register(r'gateway-config', GatewayConfigViewSet, basename='gateway-config')
router.register(r'pix-config', PixConfigViewSet, basename='pix-config')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-accounts')
router.register(r'withdraw-requests', WithdrawRequestViewSet, basename='withdraw-requests')

urlpatterns = [
    # Coloque caminhos específicos ANTES do include(router) para não conflitar com detail routes
    path('payment-links/latest/', PaymentLinkLatestView.as_view(), name='payment-link-latest'),
    path('virtual-account/balance/', VirtualAccountBalanceView.as_view(), name='virtual-account-balance'),
    path('', include(router.urls)),
]


