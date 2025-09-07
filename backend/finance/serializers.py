from rest_framework import serializers
from .models.GatewayConfig import GatewayConfig
from .models.Transaction import Transaction
from .models.PaymentLink import PaymentLink
from network.models.ScoreReference import ScoreReference


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
    licensed_username = serializers.SerializerMethodField()
    adesion_id = serializers.SerializerMethodField()
    origin_app = serializers.SerializerMethodField()
    origin_model = serializers.SerializerMethodField()
    origin_id = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'virtual_account', 'product', 'description', 'status',
            'operation', 'amount', 'is_processed', 'reference_date', 'dtt_record',
            'licensed_username', 'adesion_id',
            'origin_app', 'origin_model', 'origin_id'
        ]

    def get_licensed_username(self, obj):
        try:
            return getattr(getattr(obj.virtual_account, 'licensed', None).user, 'username', None)
        except Exception:
            return None

    def get_adesion_id(self, obj):
        # Tenta extrair o ID do PlanAdesion do campo product quando seguir padrão
        try:
            text = obj.product or ''
            # exemplos: "Plano Adesão MMN: 16" ou "Plano Adesão: Id 16"
            import re
            m = re.search(r'(?:Id\s*)?(\d+)$', text.strip())
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return None

    def _find_related_score(self, obj):
        try:
            lic = getattr(obj.virtual_account, 'licensed', None)
            if not lic:
                return None
            # Busca ScoreReference do mesmo recebedor na mesma data de referência
            qs = ScoreReference.objects.filter(receiver_licensed=lic)
            if obj.reference_date:
                qs = qs.filter(created_at__date=obj.reference_date)
            return qs.order_by('-created_at').first()
        except Exception:
            return None

    def get_origin_app(self, obj):
        sc = self._find_related_score(obj)
        try:
            return getattr(getattr(sc, 'content_type', None), 'app_label', None) if sc else None
        except Exception:
            return None

    def get_origin_model(self, obj):
        sc = self._find_related_score(obj)
        try:
            return getattr(getattr(sc, 'content_type', None), 'model', None) if sc else None
        except Exception:
            return None

    def get_origin_id(self, obj):
        sc = self._find_related_score(obj)
        try:
            return getattr(sc, 'object_id', None) if sc else None
        except Exception:
            return None


class PaymentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLink
        fields = [
            'id', 'licensed', 'adesion', 'product', 'gateway', 'order_id', 'code', 'charge_id',
            'payment_method', 'amount', 'paid_amount', 'installments', 'status', 'url', 'barcode',
            'qrcode', 'is_captured', 'is_canceled', 'created_at', 'updated_at', 'closed_at', 'canceled_at'
        ]

