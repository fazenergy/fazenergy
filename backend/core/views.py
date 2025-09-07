from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models.User import User
from .models.Licensed import Licensed
from .serializers import (
    LicensedSerializer,
    UserProfileSerializer,
    LicensedListSerializer,
    DownlineListSerializer,
    LicensedDocumentSerializer,
    AdminUserSerializer,
    AdminGroupSerializer,
    AdminPermissionSerializer,
)
from network.models import UnilevelNetwork
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt   
from django.utils import timezone
from rest_framework import viewsets, permissions as drf_permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from core.models.LicensedDocument import LicensedDocument
from django.db import models
from django.contrib.auth.models import Group, Permission

User = get_user_model()

class LicensedViewSet(viewsets.ModelViewSet):
    queryset = Licensed.objects.select_related('user', 'plan', 'city_lookup', 'current_career').all()
    serializer_class = LicensedSerializer

    def get_serializer_class(self):
        # Usa uma lista mais leve para listagem
        if getattr(self, 'action', None) == 'list':
            return LicensedListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# --------------------------- Admin Views ---------------------------
class IsSuperAdmin(drf_permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(getattr(u, 'is_superuser', False))


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class AdminGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = AdminGroupSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class AdminPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
    serializer_class = AdminPermissionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class LicensedDocumentViewSet(viewsets.ModelViewSet):
    queryset = LicensedDocument.objects.select_related('licensed').order_by('-dtt_record')
    serializer_class = LicensedDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        if is_operator:
            # Operadores enxergam tudo e podem filtrar por licenciado e status
            licensed_id = self.request.query_params.get('licensed')
            licensed_username = self.request.query_params.get('licensed_username')
            status_param = self.request.query_params.get('status')
            if licensed_id:
                qs = qs.filter(licensed_id=licensed_id)
            if licensed_username:
                qs = qs.filter(licensed__user__username__iexact=licensed_username)
            if status_param in {'pending', 'approved', 'rejected'}:
                qs = qs.filter(stt_validate=status_param)
            return qs
        # Licenciado só vê os próprios
        try:
            lic = Licensed.objects.get(user=user)
            return qs.filter(licensed=lic)
        except Licensed.DoesNotExist:
            return qs.none()

    def perform_create(self, serializer):
        # Garantir que licenciado só crie para si
        user = self.request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        lic = None
        if not is_operator:
            lic = Licensed.objects.filter(user=user).first()
            if not lic:
                raise ValidationError({'detail': 'Usuário atual não possui perfil de Licenciado.'})
        else:
            lic = serializer.validated_data.get('licensed')
            if not lic:
                raise ValidationError({'licensed': ['Este campo é obrigatório para operadores.']})
        serializer.save(licensed=lic)

    def perform_update(self, serializer):
        user = self.request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        instance = self.get_object()

        if not is_operator:
            # Licenciado não pode alterar status; se alterar arquivo/observação, força pendente
            validated = dict(serializer.validated_data)
            validated.pop('stt_validate', None)
            validated.pop('rejection_reason', None)
            # Se enviou novo arquivo ou mexeu na observação -> volta pendente
            if 'file' in validated or 'observation' in validated:
                validated['stt_validate'] = 'pending'
                validated['rejection_reason'] = None
            for k, v in validated.items():
                setattr(instance, k, v)
            instance.save()
            return

        # Operador pode atualizar normalmente (inclusive status)
        serializer.save()

    @action(detail=False, methods=['get'], url_path='pending', permission_classes=[IsAuthenticated])
    def list_pending(self, request):
        user = request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        if not is_operator:
            return Response([], status=200)
        # Documentos com status pendente de qualquer licenciado
        qs = self.get_queryset().filter(stt_validate='pending')[:50]
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)
   
# recebe a json de dados do frontend para persistencia
class LicensedPreRegisterView(generics.CreateAPIView):
    queryset = Licensed.objects.all()
    serializer_class = LicensedSerializer
    permission_classes = [AllowAny]


class DirectLicensedListView(generics.ListAPIView):
    serializer_class = LicensedListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Permite filtrar por um upline específico (desde que esteja na subárvore do usuário logado)
        user = self.request.user
        try:
            current_licensed = Licensed.objects.select_related('user').get(user=user)
        except Licensed.DoesNotExist:
            return Licensed.objects.none()

        upline_param = self.request.query_params.get('upline') or self.request.query_params.get('upline_username')
        target_upline = None

        if upline_param:
            # Aceita id numérico (Licensed.id) ou username
            if str(upline_param).isdigit():
                target_upline = Licensed.objects.filter(id=int(upline_param)).first()
            if target_upline is None:
                target_upline = Licensed.objects.filter(user__username__iexact=str(upline_param)).first()

            # Segurança: só permite se o alvo for o próprio usuário ou estiver na sua subárvore
            if target_upline and target_upline != current_licensed:
                in_subtree = UnilevelNetwork.objects.filter(
                    upline_licensed=current_licensed,
                    downline_licensed=target_upline,
                ).exists()
                if not in_subtree:
                    # Fora da subárvore: retorna vazio
                    return Licensed.objects.none()
        else:
            target_upline = current_licensed

        return (
            Licensed.objects
            .filter(original_indicator=target_upline)
            .select_related('user', 'plan', 'city_lookup', 'original_indicator')
            .order_by('-dtt_record')
        )


class DownlineTreeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DownlineListSerializer

    def list(self, request, *args, **kwargs):
        """Lista a rede completa.
        - Admin (superuser/staff/grupo Administrador) sem target: retorna a rede inteira (todas as raízes e níveis).
        - Admin/Operador com target: retorna toda a subárvore do target (todos os níveis).
        - Usuário comum: retorna toda a sua subárvore (todos os níveis).
        """
        user = request.user
        from core.models.Licensed import Licensed

        is_admin = (
            getattr(user, 'is_superuser', False)
            or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Administrador').exists()
        )

        q_target = request.query_params.get('target')

        # Caso admin sem target: retornar a rede completa (floresta)
        if is_admin and not q_target:
            relations = (
                UnilevelNetwork.objects
                .filter(level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )

            adjacency = {}
            upline_username = {}
            upline_ids, downline_ids = set(), set()
            for r in relations:
                upline_ids.add(r.upline_licensed_id)
                downline_ids.add(r.downline_licensed_id)
                adjacency.setdefault(r.upline_licensed_id, []).append(r.downline_licensed)
                upline_username[r.downline_licensed_id] = r.upline_licensed.user.username

            roots_declared = set(Licensed.objects.filter(is_root=True).values_list('id', flat=True))
            computed_roots = (upline_ids - downline_ids) if upline_ids else set()
            root_ids = (roots_declared | computed_roots)

            levels = {}
            uplines = {}
            collected_ids = set()

            # BFS por toda a floresta; nível 0 para cada raiz
            from collections import deque
            queue = deque()
            for rid in root_ids:
                queue.append((rid, 0))
                collected_ids.add(rid)
                levels[rid] = 0

            while queue:
                node_id, lvl = queue.popleft()
                for child in adjacency.get(node_id, []):
                    cid = child.id
                    if cid in collected_ids:
                        continue
                    collected_ids.add(cid)
                    levels[cid] = lvl + 1
                    uplines[cid] = upline_username.get(cid)
                    queue.append((cid, lvl + 1))

            qs = Licensed.objects.filter(id__in=collected_ids).select_related('user', 'plan', 'city_lookup')
            serializer = self.get_serializer(qs, many=True, context={'levels': levels, 'uplines': uplines})
            return Response(serializer.data)

        # Para operador/admin com target, ou usuários comuns: resolve o Licensed alvo
        target = None
        if q_target:
            target = Licensed.objects.filter(user__username__iexact=q_target).first()

        if target is None:
            try:
                target = Licensed.objects.select_related('user').get(user=user)
            except Licensed.DoesNotExist:
                return Response([], status=200)

        # BFS sem limite de níveis a partir do target
        levels = {}
        uplines = {}
        collected_ids = set()
        frontier = [target]
        current_level = 1
        while frontier:
            rels = (
                UnilevelNetwork.objects
                .filter(upline_licensed__in=frontier, level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )
            next_frontier = []
            for r in rels:
                did = r.downline_licensed_id
                if did not in collected_ids:
                    levels[did] = current_level
                    uplines[did] = r.upline_licensed.user.username
                    collected_ids.add(did)
                    next_frontier.append(r.downline_licensed)
            frontier = next_frontier
            current_level += 1

        qs = Licensed.objects.filter(id__in=collected_ids).select_related('user', 'plan', 'city_lookup')
        serializer = self.get_serializer(qs, many=True, context={'levels': levels, 'uplines': uplines})
        return Response(serializer.data)


class LicensedLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = (request.query_params.get('q') or '').strip()
        if not term:
            return Response([], status=200)

        qs = (
            Licensed.objects
            .select_related('user')
            .filter(
                models.Q(user__username__icontains=term)
                | models.Q(user__first_name__icontains=term)
                | models.Q(user__last_name__icontains=term)
            )
            .order_by('user__username')[:20]
        )
        data = [
            {
                'id': lic.id,
                'username': getattr(lic.user, 'username', None),
                'full_name': f"{getattr(lic.user, 'first_name', '')} {getattr(lic.user, 'last_name', '')}".strip(),
            }
            for lic in qs
        ]
        return Response(data)

@require_GET
@csrf_exempt
def validate_referrer(request, username):
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"valid": exists})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from core.models.Licensed import Licensed
        from django.db.models import Q

        is_admin = (
            getattr(user, 'is_superuser', False)
            or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Administrador').exists()
        )
        is_operator = user.groups.filter(name='Operador').exists()

        now = timezone.now()
        last_30_days = now - timezone.timedelta(days=30)

        # Filtro por UF (estado) opcional: ?state=SP
        state_param = (request.query_params.get('state') or '').strip().upper()
        by_state_filter = {}
        if state_param:
            # Licensed -> city_lookup -> state.uf
            by_state_filter = {'city_lookup__state__uf__iexact': state_param}

        data = {
            'role': 'admin' if is_admin else ('operator' if is_operator else 'licensed'),
            'cards': [],
            'quickActions': [],
        }

        if is_admin or is_operator:
            # Base por UF (quando aplicável)
            base_licensed_qs = Licensed.objects.filter(**by_state_filter)

            # Total de licenciados: apenas quem possui adesões pagas (confirmadas)
            from plans.models.PlanAdesion import PlanAdesion
            paid_adesions_qs = PlanAdesion.objects.filter(ind_payment_status='confirmed')
            if state_param:
                paid_adesions_qs = paid_adesions_qs.filter(
                    licensed__licensed__city_lookup__state__uf__iexact=state_param
                )
            total_licensed = (
                base_licensed_qs
                .filter(user__in=paid_adesions_qs.values('licensed_id'))
                .distinct()
                .count()
            )

            # Estatísticas auxiliares
            roots_count = base_licensed_qs.filter(is_root=True).count()
            new_licensed_30d = base_licensed_qs.filter(dtt_record__gte=last_30_days).count()
            # A contagem de arestas da rede não é trivialmente particionável por estado; mantemos total
            network_edges = UnilevelNetwork.objects.count()

            # Métricas Operador
            from finance.models.Transaction import Transaction
            from network.models.ScoreReference import ScoreReference

            # Adesões confirmadas, filtradas por UF do licenciado quando informado
            adesoes_pagas = PlanAdesion.objects.filter(ind_payment_status='confirmed')
            if state_param:
                # PlanAdesion.licensed aponta para User. Precisamos relacionar com Licensed pelo user
                adesoes_pagas = adesoes_pagas.filter(
                    licensed__licensed__city_lookup__state__uf__iexact=state_param
                )
            # Valor total pago = soma dos preços dos planos confirmados
            try:
                from plans.models.Plan import Plan
                adesoes_valor_total = (
                    Plan.objects.filter(adesions__in=adesoes_pagas)
                    .aggregate(total=models.Sum('price'))['total'] or 0
                )
            except Exception:
                adesoes_valor_total = 0
            try:
                # Caso exista Transaction para adesões com amount, somar
                adesoes_valor_total = (
                    Transaction.objects
                    .filter(product__icontains='Adesão', status='released', operation='credit')
                    .aggregate(total=models.Sum('amount'))['total'] or 0
                )
            except Exception:
                adesoes_valor_total = 0

            # Usinas pagas (quantidade): considerar PlanAdesion com product preenchido e confirmado
            usinas_pagas_qtd = adesoes_pagas.exclude(product__isnull=True).count()

            # Bônus gerados: somatório liberado (transactions credit released)
            bonus_total = 0
            try:
                bonus_qs = Transaction.objects.filter(status='released', operation='credit')
                if state_param:
                    # Transação -> VirtualAccount -> Licensed -> City.state.uf
                    bonus_qs = bonus_qs.filter(
                        virtual_account__licensed__city_lookup__state__uf__iexact=state_param
                    )
                bonus_total = bonus_qs.aggregate(total=models.Sum('amount'))['total'] or 0
            except Exception:
                bonus_total = 0

            # Pontos gerados: ScoreReference válidos
            pontos_qs = ScoreReference.objects.filter(status='valid')
            if state_param:
                pontos_qs = pontos_qs.filter(
                    receiver_licensed__city_lookup__state__uf__iexact=state_param
                )
            pontos_total = pontos_qs.aggregate(total=models.Sum('points_amount'))['total'] or 0

            data['cards'] = [
                {'key': 'total_licensed', 'title': 'Total de Licenciados', 'value': total_licensed, 'icon': 'Users', 'delta': f"+{new_licensed_30d} nos últimos 30 dias", 'route': '/network/downlines'},
                {'key': 'operator_paid_adesions', 'title': 'Adesões Pagas', 'value': float(adesoes_valor_total), 'icon': 'DollarSign', 'delta': None, 'route': '/reports/adesions'},
                {'key': 'operator_paid_plants', 'title': 'Usinas Pagas', 'value': usinas_pagas_qtd, 'icon': 'Factory', 'delta': None, 'route': '/reports/plants'},
                {'key': 'operator_bonus_total', 'title': 'Bônus Gerados', 'value': float(bonus_total), 'icon': 'Coins', 'delta': None, 'route': '/reports/bonus'},
                {'key': 'operator_points_total', 'title': 'Pontos Gerados', 'value': pontos_total, 'icon': 'Star', 'delta': None, 'route': '/reports/points'},
            ]

            data['quickActions'] = [
                {'label': 'Árvore da Rede', 'route': '/network/tree'},
                {'label': 'Rede Completa', 'route': '/network/downlines'},
                {'label': 'Revisar Documentos', 'route': '/documents/review'},
            ]

            # Relatório sintético
            # Pré-Cadastros (30d): somente licenciados com adesões NÃO pagas (pending/canceled) nos últimos 30 dias
            unpaid_adesions = PlanAdesion.objects.exclude(ind_payment_status='confirmed')
            if state_param:
                unpaid_adesions = unpaid_adesions.filter(
                    licensed__licensed__city_lookup__state__uf__iexact=state_param
                )
            pre_cadastros = (
                base_licensed_qs
                .filter(dtt_record__gte=last_30_days)
                .filter(user__in=unpaid_adesions.values('licensed_id'))
                # garante que não possui nenhuma confirmada
                .exclude(user__in=paid_adesions_qs.values('licensed_id'))
                .distinct()
                .count()
            )

            # Ativações: usuários com adesão paga há mais de 20 dias
            paid_20_days_ago = PlanAdesion.objects.filter(
                ind_payment_status='confirmed',
                dtt_payment__lte=now - timezone.timedelta(days=20)
            )
            if state_param:
                paid_20_days_ago = paid_20_days_ago.filter(
                    licensed__licensed__city_lookup__state__uf__iexact=state_param
                )
            ativacoes = (
                base_licensed_qs
                .filter(user__in=paid_20_days_ago.values('licensed_id'))
                .distinct()
                .count()
            )
            try:
                from finance.models.Transaction import Transaction
                saque_qs = Transaction.objects.filter(product__icontains='Saque', operation='debit')
                if state_param:
                    saque_qs = saque_qs.filter(
                        virtual_account__licensed__city_lookup__state__uf__iexact=state_param
                    )
                solicitacoes_saque = saque_qs.count()
            except Exception:
                solicitacoes_saque = 0
            data['summary'] = {
                'pre_registers': pre_cadastros,
                'activations': ativacoes,
                'withdraw_requests': solicitacoes_saque,
            }
            return Response(data)

        # Licensed
        try:
            current_licensed = Licensed.objects.select_related('user').get(user=user)
        except Licensed.DoesNotExist:
            return Response(data)

        directs_count = Licensed.objects.filter(original_indicator=current_licensed).count()

        # Conta toda a subárvore
        collected_ids = set()
        frontier = [current_licensed]
        level = 0
        while frontier:
            rels = (
                UnilevelNetwork.objects
                .filter(upline_licensed__in=frontier, level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )
            next_frontier = []
            for r in rels:
                did = r.downline_licensed_id
                if did not in collected_ids:
                    collected_ids.add(did)
                    next_frontier.append(r.downline_licensed)
            frontier = next_frontier
            level += 1

        team_size = len(collected_ids)
        active_team = Licensed.objects.filter(id__in=collected_ids, stt_record=True).count()

        data['cards'] = [
            {'key': 'directs', 'title': 'Diretos', 'value': directs_count, 'icon': 'UserPlus', 'delta': None},
            {'key': 'team_size', 'title': 'Minha Rede', 'value': team_size, 'icon': 'Users', 'delta': None},
            {'key': 'career', 'title': 'Carreira Atual', 'value': (current_licensed.current_career.stage_name if current_licensed.current_career else '-'), 'icon': 'TrendingUp', 'delta': None},
            {'key': 'docs_status', 'title': 'Documentação', 'value': current_licensed.stt_document.capitalize(), 'icon': 'File', 'delta': None},
        ]

        data['quickActions'] = [
            {'label': 'Cadastrar Licenciado', 'route': '/preRegister'},
            {'label': 'Árvore da Rede', 'route': '/network/tree'},
            {'label': 'Enviar Documentos', 'route': '/documents'},
        ]

        # Banner de documentos pendentes para licenciados
        data['documents'] = {
            'status': current_licensed.stt_document,
            'pending': current_licensed.stt_document == 'pending'
        }

        # Billing banner: se não é raiz, tem adesão pendente e não é cortesia
        try:
            from plans.models.PlanAdesion import PlanAdesion
            from finance.models.PaymentLink import PaymentLink
            last_adesion = (
                PlanAdesion.objects
                .filter(licensed=user)
                .order_by('-dtt_record')
                .first()
            )
            pending = False
            pay_url = None
            adesion_id = None
            if last_adesion:
                adesion_id = last_adesion.id
                if not current_licensed.is_root and not last_adesion.is_courtesy and last_adesion.ind_payment_status != 'confirmed':
                    pending = True
                    pl = PaymentLink.objects.filter(adesion=last_adesion).order_by('-created_at').first()
                    pay_url = getattr(pl, 'url', None) if pl else None
            data['billing'] = {
                'pending_annual_payment': pending,
                'payment_link_url': pay_url,
                'adesion_id': adesion_id,
            }
        except Exception:
            data['billing'] = {
                'pending_annual_payment': False,
                'payment_link_url': None,
                'adesion_id': None,
            }

        return Response(data)
