from rest_framework import serializers
from .models.GatewayConfig import GatewayConfig
from .models.Transaction import Transaction
from .models.PaymentLink import PaymentLink


class GatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayConfig
        fields = [
            'id', 'name', 'api_token', 'api_url', 'dev_url_hint',
            'postback_url', 'redirect_url',
            'webhook_token', 'webhook_user', 'webhook_password', 'webhook_secret',
            'active'
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'virtual_account', 'product', 'description', 'status',
            'operation', 'amount', 'is_processed', 'reference_date', 'dtt_record'
        ]


class PaymentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLink
        fields = [
            'id', 'licensed', 'adesion', 'product', 'gateway', 'order_id', 'code', 'charge_id',
            'payment_method', 'amount', 'paid_amount', 'installments', 'status', 'url', 'barcode',
            'qrcode', 'is_captured', 'is_canceled', 'created_at', 'updated_at', 'closed_at', 'canceled_at'
        ]

