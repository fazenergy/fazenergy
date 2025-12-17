from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models.GatewayConfig import GatewayConfig
from .models.Transaction import Transaction
from .models.PaymentLink import PaymentLink
from .serializers import (
    GatewayConfigSerializer, TransactionSerializer, PaymentLinkSerializer,
    BankAccountSerializer, WithdrawRequestSerializer, PixConfigSerializer,
    WithdrawRequestLogSerializer
)
from .models.VirtualAccount import VirtualAccount
from .models import BankAccount, WithdrawRequest, WithdrawRequestLog
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import Group
from core.models.Licensed import Licensed
from rest_framework.decorators import action
from .services.withdraw import process_withdraw_request
from .models.PixConfig import PixConfig


class GatewayConfigViewSet(viewsets.ModelViewSet):
    queryset = GatewayConfig.objects.all()
    serializer_class = GatewayConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        instance = GatewayConfig.objects.first()
        if not instance:
            # Garante um registro default para a UI preencher
            instance = GatewayConfig.objects.create(
                name='Pagarme',
                api_token='',
                api_url='https://sdx-api.pagar.me/core/v5/paymentlinks',
                active=True,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PixConfigViewSet(viewsets.ModelViewSet):
    queryset = PixConfig.objects.all()
    serializer_class = PixConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        instance = PixConfig.objects.first()
        if not instance:
            # Defaults para facilitar testes no sandbox Sicoob
            instance = PixConfig.objects.create(
                provider_name='Sicoob',
                api_base_url='https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2',
                oauth_url='',
                client_id='9b5e603e428cc477a2841e2683c92d21',
                client_secret='',
                access_token='1301865f-c6bc-38f3-9f49-666dbcfc59c3',
                cert_path='',
                key_path='',
                active=True,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related('virtual_account__licensed__user').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtros opcionais: licensed_username, month, year
        licensed_username = self.request.query_params.get('licensed_username')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if licensed_username:
            qs = qs.filter(virtual_account__licensed__user__username__iexact=licensed_username)
        from django.db.models.functions import ExtractMonth, ExtractYear
        if year:
            qs = qs.annotate(y=ExtractYear('reference_date')).filter(y=int(year))
        if month:
            qs = qs.annotate(m=ExtractMonth('reference_date')).filter(m=int(month))
        return qs.order_by('-reference_date', '-dtt_record')

    def create(self, request, *args, **kwargs):
        """
        Cria uma transação administrativa (crédito/débito) na conta virtual do licenciado
        e atualiza o saldo disponível imediatamente.
        Campos aceitos: licensed_username, operation (credit|debit), amount, description (opcional).
        Permissão: superadmin ou operador.
        """
        user = request.user
        is_admin = getattr(user, 'is_superuser', False)
        is_operator = user.groups.filter(name='Operador').exists() or getattr(user, 'is_staff', False)
        if not (is_admin or is_operator):
            return Response({'detail': 'Sem permissão.'}, status=status.HTTP_403_FORBIDDEN)

        licensed_username = (request.data.get('licensed_username') or '').strip()
        operation = (request.data.get('operation') or '').strip().lower()
        raw_amount = request.data.get('amount')
        extra_desc = (request.data.get('description') or '').strip()

        if not licensed_username:
            return Response({'licensed_username': 'Obrigatório.'}, status=400)
        if operation not in ('credit', 'debit'):
            return Response({'operation': 'Use "credit" ou "debit".'}, status=400)
        try:
            amount = Decimal(str(raw_amount))
            if amount <= 0:
                raise InvalidOperation()
        except Exception:
            return Response({'amount': 'Valor inválido (use número maior que zero).'}, status=400)

        # Localiza licenciado e conta virtual
        try:
            licensed = Licensed.objects.select_related('user').get(user__username__iexact=licensed_username)
        except Licensed.DoesNotExist:
            return Response({'licensed_username': 'Usuário não encontrado.'}, status=404)

        va, _ = VirtualAccount.objects.get_or_create(
            licensed=licensed,
            defaults={'name_licensed': licensed.user.username}
        )

        now = timezone.now()
        op_label = 'Crédito' if operation == 'credit' else 'Débito'
        composed_desc = (
            f"{op_label} lançado via usuário operador {user.username} em {now.strftime('%d/%m/%Y %H:%M')} "
            f"para o usuário {licensed.user.username}."
        )
        if extra_desc:
            composed_desc += f" {extra_desc}"

        tx = Transaction.objects.create(
            virtual_account=va,
            product='Transação Administrativa',
            description=composed_desc,
            status='released',
            operation=operation,
            amount=amount,
            is_processed=True,
            reference_date=now.date(),
        )

        # Atualiza saldo disponível
        if operation == 'credit':
            va.balance_available = (va.balance_available or Decimal('0')) + amount
        else:
            va.balance_available = (va.balance_available or Decimal('0')) - amount
        va.save(update_fields=['balance_available', 'dtt_update'])

        serializer = self.get_serializer(tx)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PaymentLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentLink.objects.select_related('licensed', 'adesion').all()
    serializer_class = PaymentLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        adesion_id = self.request.query_params.get('adesion')
        if adesion_id:
            qs = qs.filter(adesion_id=adesion_id)
        return qs

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class PaymentLinkLatestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        adesion_id = request.query_params.get('adesion')
        licensed_username = request.query_params.get('licensed_username')
        qs = PaymentLink.objects.all()
        if adesion_id:
            qs = qs.filter(adesion_id=adesion_id)
        elif licensed_username:
            qs = qs.filter(licensed__user__username__iexact=licensed_username)
        else:
            return Response({'detail': 'informe adesion ou licensed_username'}, status=400)
        qs = qs.order_by('-created_at')
        obj = qs.first()
        if not obj:
            return Response(None, status=204)
        serializer = PaymentLinkSerializer(obj)
        return Response(serializer.data)


class VirtualAccountBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        licensed_username = request.query_params.get('licensed_username')
        licensed_id = request.query_params.get('licensed_id')
        qs = VirtualAccount.objects.select_related('licensed__user')
        if licensed_username:
            qs = qs.filter(licensed__user__username__iexact=licensed_username)
        elif licensed_id:
            qs = qs.filter(licensed_id=licensed_id)
        else:
            # saldo do usuário atual
            qs = qs.filter(licensed__user=request.user)

        va = qs.first()
        if not va:
            return Response({'balance_available': 0.0, 'balance_blocked': 0.0})

        return Response({
            'balance_available': float(va.balance_available),
            'balance_blocked': float(va.balance_blocked),
            'licensed_username': getattr(getattr(va.licensed, 'user', None), 'username', None)
        })


class BankAccountViewSet(viewsets.ModelViewSet):
    """CRUD de contas bancárias do próprio licenciado.

    Regras de permissão:
    - Listar: retorna apenas contas do usuário autenticado.
    - Criar/Editar/Excluir: somente do próprio usuário.
    - Operador/Superadmin podem listar por `?licensed_id=` para auxílio, se necessário.
    """
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = BankAccount.objects.select_related('licensed__user', 'company')
        user = self.request.user
        if user.is_superuser or user.is_staff or user.groups.filter(name='Operador').exists():
            licensed_id = self.request.query_params.get('licensed_id')
            if licensed_id:
                return qs.filter(licensed_id=licensed_id)
        return qs.filter(licensed__user=user)

    def perform_destroy(self, instance):
        # Impede apagar conta usada em saque pendente
        if WithdrawRequest.objects.filter(bank_account=instance, status='pending').exists():
            raise Exception('Conta vinculada a solicitação de saque pendente.')
        super().perform_destroy(instance)


class WithdrawRequestViewSet(viewsets.ModelViewSet):
    """API para solicitações de saque do licenciado.

    Criação aplica validações de saldo, valor mínimo e bloqueia duplicidade pendente.
    """
    serializer_class = WithdrawRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = WithdrawRequest.objects.select_related('bank_account', 'licensed__user')
        user = self.request.user
        if user.is_superuser or user.is_staff or user.groups.filter(name='Operador').exists():
            licensed_id = self.request.query_params.get('licensed_id')
            if licensed_id:
                return qs.filter(licensed_id=licensed_id)
        status_param = (self.request.query_params.get('status') or '').strip()
        qs = qs.filter(licensed__user=user)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Processa uma solicitação de saque pendente via PIX Sicoob.

        - Valida permissões (somente superadmin/operador).
        - Aciona serviço que valida janela permitida, debita saldo e integra com Sicoob PIX.
        - Atualiza status para paid/rejected conforme resposta.
        """
        user = request.user
        is_admin_or_operator = (
            getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Operador').exists()
        )
        if not is_admin_or_operator:
            return Response({'detail': 'Sem permissão para processar.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            obj = self.get_queryset().get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)

        result = process_withdraw_request(obj, actor_username=user.username)
        resp = {
            'ok': result.ok,
            'status': result.status,
            'message': result.message,
            'provider_payload': result.provider_payload,
        }
        return Response(resp, status=200 if result.ok else 400)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprova a solicitação (sem disparar pagamento) e define previsão de pagamento.

        Permissões: operador/superadmin.
        Body opcional: expected_payout_date (YYYY-MM-DD).
        """
        user = request.user
        is_admin_or_operator = (
            getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Operador').exists()
        )
        if not is_admin_or_operator:
            return Response({'detail': 'Sem permissão.'}, status=403)
        try:
            obj = WithdrawRequest.objects.select_related('licensed').get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)
        if obj.status not in ('pending', 'scheduled'):
            return Response({'detail': 'Somente pendente ou já agendado podem ser aprovados.'}, status=400)
        from django.utils.dateparse import parse_date
        expected = request.data.get('expected_payout_date')
        obj.approved_by = user
        obj.approved_at = timezone.now()
        if expected:
            obj.expected_payout_date = parse_date(str(expected))
        obj.save(update_fields=['approved_by', 'approved_at', 'expected_payout_date'])
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=obj, action='approved', actor=user, note='Aprovação registrada.'
            )
        except Exception:
            pass
        return Response({'ok': True, 'status': obj.status, 'expected_payout_date': obj.expected_payout_date}, status=200)

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Agenda a solicitação para processamento futuro (sem chamar Sicoob agora).

        Permissões: operador/superadmin.
        Body: scheduled_for (ISO datetime) e expected_payout_date (YYYY-MM-DD, opcional).
        """
        user = request.user
        is_admin_or_operator = (
            getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Operador').exists()
        )
        if not is_admin_or_operator:
            return Response({'detail': 'Sem permissão.'}, status=403)
        try:
            obj = WithdrawRequest.objects.select_related('licensed').get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)
        if obj.status not in ('pending', 'rejected'):
            return Response({'detail': 'Somente pendente ou rejeitada podem ser agendadas.'}, status=400)
        from django.utils.dateparse import parse_datetime, parse_date
        scheduled_for = request.data.get('scheduled_for')
        expected = request.data.get('expected_payout_date')
        dt = parse_datetime(str(scheduled_for)) if scheduled_for else None
        if not dt:
            return Response({'scheduled_for': 'Informe data/hora válida para agendamento (ISO).'}, status=400)
        obj.status = 'scheduled'
        obj.scheduled_for = dt
        obj.scheduled_by = user
        if expected:
            obj.expected_payout_date = parse_date(str(expected))
        obj.save(update_fields=['status', 'scheduled_for', 'scheduled_by', 'expected_payout_date'])
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=obj, action='scheduled', actor=user, note=f'Agendado para {dt.isoformat()}'
            )
        except Exception:
            pass
        return Response({'ok': True, 'status': obj.status, 'scheduled_for': obj.scheduled_for, 'expected_payout_date': obj.expected_payout_date}, status=200)

    @action(detail=True, methods=['post'])
    def emergency_release(self, request, pk=None):
        """Liberação emergencial: processa imediatamente via Sicoob, exigindo motivo.

        - Ignora janela (_bypass_window=True).
        - Registra motivo em emergency_reason e loga ação.
        """
        user = request.user
        is_admin_or_operator = (
            getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Operador').exists()
        )
        if not is_admin_or_operator:
            return Response({'detail': 'Sem permissão.'}, status=403)
        try:
            obj = WithdrawRequest.objects.select_related('licensed').get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)
        reason = (request.data.get('reason') or '').strip()
        if not reason:
            return Response({'reason': 'Informe o motivo da liberação emergencial.'}, status=400)
        obj.emergency_reason = reason
        obj.save(update_fields=['emergency_reason'])
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=obj, action='emergency_released', actor=user, note=reason
            )
        except Exception:
            pass
        result = process_withdraw_request(obj, actor_username=user.username, bypass_window=True)
        resp = {
            'ok': result.ok,
            'status': result.status,
            'message': result.message,
            'provider_payload': result.provider_payload,
        }
        return Response(resp, status=200 if result.ok else 400)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela uma solicitação agendada/pendente.

        Permissões: operador/superadmin para qualquer; licenciado pode cancelar as próprias se ainda pendentes.
        """
        user = request.user
        try:
            obj = WithdrawRequest.objects.select_related('licensed__user').get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)

        is_admin_or_operator = (
            getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Operador').exists()
        )
        if not is_admin_or_operator and obj.licensed.user_id != user.id:
            return Response({'detail': 'Sem permissão.'}, status=403)
        if obj.status not in ('pending', 'scheduled'):
            return Response({'detail': 'Somente pendente/agendado podem ser cancelados.'}, status=400)
        reason = (request.data.get('reason') or '').strip() or 'Cancelado pelo usuário/operador.'
        from django.utils import timezone as tz
        obj.status = 'canceled'
        obj.canceled_by = user
        obj.canceled_at = tz.now()
        obj.cancel_reason = reason
        obj.save(update_fields=['status', 'canceled_by', 'canceled_at', 'cancel_reason'])
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=obj, action='canceled', actor=user, note=reason
            )
        except Exception:
            pass
        return Response({'ok': True, 'status': obj.status}, status=200)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        try:
            obj = WithdrawRequest.objects.get(pk=pk)
        except WithdrawRequest.DoesNotExist:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)
        logs = WithdrawRequestLog.objects.filter(withdraw_request=obj).order_by('created_at')
        ser = WithdrawRequestLogSerializer(logs, many=True)
        return Response(ser.data)

