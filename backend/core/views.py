from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models.User import User
from .models.Licensed import Licensed
from .serializers import (
    LicensedSerializer,
    UserProfileSerializer,
    LicensedListSerializer,
    DownlineListSerializer,
)
from network.models import UnilevelNetwork
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt   
from django.utils import timezone

User = get_user_model()

class LicensedViewSet(viewsets.ModelViewSet):
    queryset = Licensed.objects.all()
    serializer_class = LicensedSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
   
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

        is_admin = (
            getattr(user, 'is_superuser', False)
            or getattr(user, 'is_staff', False)
            or user.groups.filter(name='Administrador').exists()
        )
        is_operator = user.groups.filter(name='Operador').exists()

        now = timezone.now()
        last_30_days = now - timezone.timedelta(days=30)

        data = {
            'role': 'admin' if is_admin else ('operator' if is_operator else 'licensed'),
            'cards': [],
            'quickActions': [],
        }

        if is_admin or is_operator:
            total_licensed = Licensed.objects.count()
            active_licensed = Licensed.objects.filter(stt_record=True).count()
            roots_count = Licensed.objects.filter(is_root=True).count()
            new_licensed_30d = Licensed.objects.filter(dtt_record__gte=last_30_days).count()
            network_edges = UnilevelNetwork.objects.count()

            data['cards'] = [
                {'key': 'total_licensed', 'title': 'Total de Licenciados', 'value': total_licensed, 'icon': 'UserPlus', 'delta': f"+{new_licensed_30d} nos últimos 30 dias"},
                {'key': 'active_affiliates', 'title': 'Afiliados Ativos', 'value': active_licensed, 'icon': 'UserCheck', 'delta': None},
                {'key': 'roots_count', 'title': 'Redes Raiz', 'value': roots_count, 'icon': 'Users', 'delta': None},
                {'key': 'network_edges', 'title': 'Relações na Rede', 'value': network_edges, 'icon': 'TrendingUp', 'delta': None},
            ]

            data['quickActions'] = [
                {'label': 'Árvore da Rede', 'route': '/network/tree'},
                {'label': 'Rede Completa', 'route': '/network/downlines'},
            ]
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
            {'key': 'active_team', 'title': 'Equipe Ativa', 'value': active_team, 'icon': 'UserCheck', 'delta': None},
            {'key': 'career', 'title': 'Carreira Atual', 'value': (current_licensed.current_career.stage_name if current_licensed.current_career else '-'), 'icon': 'TrendingUp', 'delta': None},
        ]

        data['quickActions'] = [
            {'label': 'Cadastrar Licenciado', 'route': '/preRegister'},
            {'label': 'Árvore da Rede', 'route': '/network/tree'},
        ]
        return Response(data)
