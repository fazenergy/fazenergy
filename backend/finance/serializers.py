from rest_framework import serializers
from .models.GatewayConfig import GatewayConfig
from .models.Transaction import Transaction
from .models.PaymentLink import PaymentLink
from .models.BankAccount import BankAccount
from .models.WithdrawRequest import WithdrawRequest
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


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer de conta bancária com validações de regra PF/PJ.

    - owner_type='pj' exige `company` e a empresa deve estar aprovada.
    - owner_type='pf' não deve enviar `company`.
    - `is_default` opcional: se verdadeiro, desmarca outras do mesmo licenciado.
    """

    class Meta:
        model = BankAccount
        fields = [
            'id', 'licensed', 'owner_type', 'company', 'bank_code', 'bank_name', 'account_type',
            'agency_number', 'agency_digit', 'account_number', 'account_digit',
            'account_holder_name', 'account_holder_cpf_cnpj', 'is_default',
            'dtt_record', 'dtt_update'
        ]
        read_only_fields = ['licensed', 'dtt_record', 'dtt_update']

    def validate(self, attrs):
        owner_type = attrs.get('owner_type') or getattr(self.instance, 'owner_type', 'pf')
        company = attrs.get('company') if 'company' in attrs else getattr(self.instance, 'company', None)
        if owner_type == 'pj':
            if not company:
                raise serializers.ValidationError({'company': 'Obrigatório para conta PJ.'})
            if getattr(company, 'stt_validate', 'pending') != 'approved':
                raise serializers.ValidationError({'company': 'Empresa precisa estar aprovada.'})
        else:
            if company is not None:
                raise serializers.ValidationError({'company': 'Para conta PF, não envie empresa.'})
        return attrs

    def create(self, validated_data):
        # força licensed atual
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            from core.models.Licensed import Licensed
            licensed = Licensed.objects.get(user=request.user)
            validated_data['licensed'] = licensed
        obj = super().create(validated_data)
        # se marcada default, desmarca as demais
        if obj.is_default:
            BankAccount.objects.filter(licensed=obj.licensed).exclude(pk=obj.pk).update(is_default=False)
        return obj

    def update(self, instance, validated_data):
        obj = super().update(instance, validated_data)
        if obj.is_default:
            BankAccount.objects.filter(licensed=obj.licensed).exclude(pk=obj.pk).update(is_default=False)
        return obj


class WithdrawRequestSerializer(serializers.ModelSerializer):
    """Serializer de solicitação de saque com validações de negócio.

    Regras:
    - impede nova solicitação quando já existir `pending` do licenciado.
    - valida valor mínimo via setting/env (fallback R$ 50,00) e saldo disponível.
    - aplica taxa fixa por solicitação (fallback R$ 10,00) e permite registrar imposto estimado.
    """

    bank_snapshot = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WithdrawRequest
        fields = [
            'id', 'licensed', 'bank_account', 'amount', 'fee_amount', 'tax_amount', 'status', 'note',
            'requested_at', 'processed_at', 'bank_snapshot'
        ]
        read_only_fields = ['licensed', 'status', 'requested_at', 'processed_at', 'fee_amount', 'tax_amount', 'bank_snapshot']

    def get_bank_snapshot(self, obj):
        try:
            ba = obj.bank_account
            return {
                'bank_code': ba.bank_code,
                'bank_name': ba.bank_name,
                'account_type': ba.account_type,
                'agency_number': ba.agency_number,
                'agency_digit': ba.agency_digit,
                'account_number': ba.account_number,
                'account_digit': ba.account_digit,
            }
        except Exception:
            return None

    def validate(self, attrs):
        request = self.context.get('request')
        from core.models.Licensed import Licensed
        licensed = Licensed.objects.get(user=request.user)

        # bloqueia múltiplas pendentes
        if WithdrawRequest.objects.filter(licensed=licensed, status='pending').exists():
            raise serializers.ValidationError({'non_field_errors': 'Já existe uma solicitação pendente. Aguarde o processamento.'})

        # valida conta pertence ao usuário
        ba = attrs.get('bank_account')
        if not ba or ba.licensed_id != licensed.id:
            raise serializers.ValidationError({'bank_account': 'Conta inválida para este usuário.'})

        # valida valor mínimo e saldo
        from decimal import Decimal
        from django.conf import settings
        min_withdraw = getattr(settings, 'WITHDRAW_MIN_VALUE', Decimal('50'))
        fee_fixed = getattr(settings, 'WITHDRAW_FEE_FIXED', Decimal('10'))
        amount = Decimal(str(attrs.get('amount') or '0'))
        if amount < min_withdraw:
            raise serializers.ValidationError({'amount': f'Valor mínimo para saque é R$ {min_withdraw}.'})

        # saldo
        from .models import VirtualAccount
        va = VirtualAccount.objects.filter(licensed=licensed).first()
        if not va or (va.balance_available or 0) < amount:
            raise serializers.ValidationError({'amount': 'Saldo insuficiente.'})

        # preenche taxas padrão
        attrs['fee_amount'] = fee_fixed
        # impostos estimados: 0 por padrão, processamento posterior pode calcular
        attrs['tax_amount'] = attrs.get('tax_amount') or 0
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        from core.models.Licensed import Licensed
        licensed = Licensed.objects.get(user=request.user)
        validated_data['licensed'] = licensed
        return super().create(validated_data)
