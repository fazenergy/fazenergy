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
    LicensedCompanySerializer,
    # Company
    # serializers para admin serão mantidos
    AdminUserSerializer,
    AdminGroupSerializer,
    AdminPermissionSerializer,
)
from core.models.LicensedCompany import LicensedCompany
from core.models.LicensedDocument import LicensedDocument
from network.models import UnilevelNetwork
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from celery.schedules import crontab
from django.utils import timezone as dj_tz

# ==== Segurança do Login (throttle + lockout) ====
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.cache import cache
from django.conf import settings
from core.models.ScheduledTaskConfig import ScheduledTaskConfig, ScheduledTaskLog
from core.serializers import ScheduledTaskConfigSerializer, ScheduledTaskLogSerializer


class SecureTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer padrão do SimpleJWT sem alteração de payload.

    A lógica de lockout é aplicada na View; mantemos o serializer padrão
    para evitar customizações desnecessárias aqui.
    """
    pass


class SecureTokenObtainPairView(TokenObtainPairView):
    """View de login com proteções:
    - Throttling por IP e por username (reduz brute-force);
    - Lockout temporário por usuário após múltiplas falhas.

    Parâmetros configuráveis via settings:
    - LOGIN_LOCKOUT_FAILURES: n° de tentativas antes do bloqueio (padrão: 5)
    - LOGIN_LOCKOUT_WINDOW: janela para contar falhas, em segundos (padrão: 900 = 15 min)
    - LOGIN_LOCKOUT_DURATION: duração do bloqueio, em segundos (padrão: 900 = 15 min)
    """

    permission_classes = [AllowAny]
    serializer_class = SecureTokenObtainPairSerializer

    def _lockout_cache_key(self, username: str) -> str:
        return f"login:lockout:{username}"

    def _fail_count_cache_key(self, username: str) -> str:
        return f"login:failcount:{username}"

    def post(self, request, *args, **kwargs):
        username = (request.data.get("username") or "").strip().lower()

        # 1) Verifica se o usuário está bloqueado
        lock_key = self._lockout_cache_key(username)
        if username and cache.get(lock_key):
            # Responde como falha genérica para não revelar lockout
            return Response({"detail": "Credenciais inválidas."}, status=401)

        # 2) Tenta autenticar via fluxo normal do SimpleJWT
        response = super().post(request, *args, **kwargs)

        # 3) Se sucesso, zera contador de falhas
        if response.status_code == 200 and username:
            # Sucesso: zera contador e retorna
            cache.delete(self._fail_count_cache_key(username))
            return response

        # 4) Se falha, incrementa contador e avalia lockout
        if username:
            failures_key = self._fail_count_cache_key(username)
            window = getattr(settings, "LOGIN_LOCKOUT_WINDOW", 900)
            max_failures = getattr(settings, "LOGIN_LOCKOUT_FAILURES", 5)
            duration = getattr(settings, "LOGIN_LOCKOUT_DURATION", 900)

            # Incrementa falhas na janela (usa add + incr para garantir ttl)
            added = cache.add(failures_key, 1, timeout=window)
            if not added:
                try:
                    cache.incr(failures_key)
                except Exception:
                    cache.set(failures_key, 1, timeout=window)

            # Verifica total e aplica lockout se necessário
            try:
                total = int(cache.get(failures_key) or 0)
            except Exception:
                total = 1

            if total >= max_failures:
                cache.set(lock_key, True, timeout=duration)

        # Resposta genérica de falha
        return Response({"detail": "Credenciais inválidas."}, status=401)

from django.views.decorators.csrf import csrf_exempt   
from django.utils import timezone
from rest_framework import viewsets, permissions as drf_permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from core.models.LicensedDocument import LicensedDocument
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from django.db import transaction

User = get_user_model()

# Registrar suporte a HEIF/AVIF no Pillow quando disponível
try:  # pillow-heif
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass
try:  # pillow-avif-plugin
    import pillow_avif  # type: ignore  # noqa: F401
except Exception:
    pass

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

    @action(detail=True, methods=['patch'], url_path='user', parser_classes=[MultiPartParser, FormParser, JSONParser], permission_classes=[IsAuthenticated])
    def update_linked_user(self, request, pk=None):
        """Permite que Operadores e Superadmins editem dados básicos do User
        vinculado ao Licensed selecionado. O próprio usuário também pode editar.

        Campos aceitos (todos opcionais): username, email, first_name, last_name,
        password, image_profile
        """
        licensed = self.get_object()
        target_user = getattr(licensed, 'user', None)
        if not target_user:
            return Response({'detail': 'Usuário não encontrado.'}, status=404)

        user = request.user
        is_admin = getattr(user, 'is_superuser', False)
        is_operator = user.groups.filter(name='Operador').exists() or getattr(user, 'is_staff', False)
        is_self = user == target_user

        if not (is_admin or is_operator or is_self):
            return Response({'detail': 'Você não tem permissão para executar essa ação.'}, status=403)

        allowed_fields = {'username', 'email', 'first_name', 'last_name'}
        data = request.data

        # Atualiza campos simples
        for f in allowed_fields:
            if f in data:
                setattr(target_user, f, data.get(f))

        # Senha opcional
        if data.get('password'):
            target_user.set_password(data.get('password'))

        # Foto opcional (com renomeação cpf-hash.extensão)
        if 'image_profile' in request.FILES:
            file = request.FILES['image_profile']
            try:
                # tenta obter cpf do Licensed relacionado (somente dígitos)
                lic = Licensed.objects.filter(user=target_user).first()
                cpf = getattr(lic, 'cpf_cnpj', '') or ''
                import re, hashlib, os, io
                from django.core.files.uploadedfile import SimpleUploadedFile
                from PIL import Image, ImageFile
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                cpf_digits = re.sub(r'\D', '', str(cpf))
                try:
                    file.seek(0)
                except Exception:
                    pass
                raw = file.read()
                # Caso content_type esteja ausente/incorreto em PNG, tenta inferir pelo header
                if not getattr(file, 'content_type', None):
                    try:
                        if raw[:8] == b'\x89PNG\r\n\x1a\n':
                            file.content_type = 'image/png'
                    except Exception:
                        pass
                # Tenta converter para JPEG para garantir validação
                try:
                    img = Image.open(io.BytesIO(raw))
                    rgb = img.convert('RGB')
                    buf = io.BytesIO()
                    rgb.save(buf, format='JPEG', quality=90)
                    file_bytes = buf.getvalue()
                    ext = '.jpg'
                    content_type = 'image/jpeg'
                except Exception:
                    # Se não conseguir converter, usa original mesmo
                    file_bytes = raw
                    ext = os.path.splitext(getattr(file, 'name', ''))[1] or '.jpg'
                    content_type = getattr(file, 'content_type', None) or 'image/jpeg'
                file_hash = hashlib.sha256(file_bytes).hexdigest()[:16]
                new_name = f"{cpf_digits}-{file_hash}{ext}"
                renamed = SimpleUploadedFile(new_name, file_bytes, content_type=content_type)
                target_user.image_profile = renamed
            except Exception:
                # fallback: ignora imagem para não travar atualização
                request._files = request._files.copy()
                try:
                    del request._files['image_profile']
                except Exception:
                    pass

        try:
            target_user.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

        return Response({'detail': 'Atualizado com sucesso.'})

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Permite multipart para upload de avatar/foto de perfil
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Sobrescreve para tratar renomeação de image_profile semelhante ao endpoint de operador."""
        user = request.user
        data = request.data

        # Se houver arquivo de imagem, aplica estratégia simples (igual à tela de edição de licenciado):
        # atribui o arquivo direto ao user antes do serializer, sem renomear/converter.
        files = request.FILES
        if 'image_profile' in files:
            try:
                user.image_profile = files['image_profile']
                user.save(update_fields=['image_profile'])
                # Remove do payload para não passar pelo serializer novamente
                request._files = request._files.copy()
                try:
                    del request._files['image_profile']
                except Exception:
                    pass
            except Exception:
                pass

        return super().update(request, *args, **kwargs)


class CurrentLicensedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lic = Licensed.objects.select_related('user', 'city_lookup__state', 'plan').get(user=request.user)
        except Licensed.DoesNotExist:
            return Response({}, status=200)
        ser = LicensedListSerializer(lic)
        return Response(ser.data)


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
    queryset = LicensedDocument.objects.select_related('licensed', 'company').order_by('-dtt_record')
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
            company_id = self.request.query_params.get('company')
            owner_type = self.request.query_params.get('owner_type')
            if company_id:
                qs = qs.filter(company_id=company_id)
            if owner_type in {'pf', 'pj'}:
                qs = qs.filter(owner_type=owner_type)
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


class LicensedCompanyViewSet(viewsets.ModelViewSet):
    queryset = LicensedCompany.objects.select_related('licensed', 'city_lookup').order_by('-dtt_record')
    serializer_class = LicensedCompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        if is_operator:
            licensed_id = self.request.query_params.get('licensed')
            status_param = self.request.query_params.get('status')
            if licensed_id:
                qs = qs.filter(licensed_id=licensed_id)
            if status_param in {'pending', 'approved', 'rejected'}:
                qs = qs.filter(stt_validate=status_param)
            return qs
        # Licenciado vê apenas as próprias empresas
        try:
            lic = Licensed.objects.get(user=user)
            return qs.filter(licensed=lic)
        except Licensed.DoesNotExist:
            return qs.none()

    def perform_create(self, serializer):
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
            # Pontos gerados (ScoreReference válidos)
            try:
                pontos_gerados = ScoreReference.objects.filter(
                    stt_record=True
                ).aggregate(
                    total=models.Sum('points')
                )['total'] or 0
            except Exception:
                pontos_gerados = 0
                
            data['summary'] = {
                'points_generated': pontos_gerados,
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

        # Pontos projetados x consolidados e projeção de bônus (conforme SCOPE: 0,10 por ponto)
        try:
            from network.models.ScoreReference import ScoreReference
            from django.db.models import Sum as DjSum
            points_projected = (
                ScoreReference.objects
                .filter(receiver_licensed=current_licensed, status='pending')
                .aggregate(total=DjSum('points_amount'))['total'] or 0
            )
            points_consolidated = (
                ScoreReference.objects
                .filter(receiver_licensed=current_licensed, status='valid')
                .aggregate(total=DjSum('points_amount'))['total'] or 0
            )
        except Exception:
            points_projected = 0
            points_consolidated = 0

        # Conversão simples ponto->R$ (R$0,10 por ponto) – ver docs/SCOPE.md
        bonus_projection_value = float(points_projected * 0.1)
        # Saldo disponível (carteira virtual)
        try:
            from finance.models.VirtualAccount import VirtualAccount
            va = VirtualAccount.objects.filter(licensed=current_licensed).first()
            balance_available = float(getattr(va, 'balance_available', 0) or 0)
        except Exception:
            balance_available = 0.0

        month_label = timezone.now().strftime('%m/%Y')

        # Usinas vendidas: propostas aprovadas do licenciado (ver docs/ScopeAquiles.md e SCOPE.md)
        try:
            from contractor.models import Proposal
            sold_plants_count = Proposal.objects.filter(
                contractor__licensed=current_licensed,
                status='Aprovado'
            ).count()
        except Exception:
            sold_plants_count = 0

        # Status de documentação PF/PJ para o card (exibição no front)
        try:
            from core.models.LicensedDocument import LicensedDocument as _LD
            from core.choices import DOCUMENT_TYPE_CHOICES as _DOC_CHOICES
            required_all = {k for k, _ in _DOC_CHOICES}
            required_pj = {'cnpj_card', 'social_contract'}
            required_pf = required_all - required_pj

            def derive_status(owner: str) -> str:
                qs = _LD.objects.filter(licensed=current_licensed, owner_type=owner)
                if not qs.exists():
                    return 'pending'
                present = set(qs.values_list('document_type', flat=True))
                req = required_pf if owner == 'pf' else required_pj
                if not req.issubset(present):
                    return 'incomplete'
                if qs.filter(stt_validate='pending').exists():
                    return 'awaiting'
                if qs.filter(stt_validate='rejected').exists():
                    return 'rejected'
                return 'approved'

            docs_map = {'pf': derive_status('pf'), 'pj': derive_status('pj')}
        except Exception:
            docs_map = {'pf': (current_licensed.stt_document or 'pending'), 'pj': 'pending'}

        data['cards'] = [
            # Sequência solicitada: Rede, Usinas Vendidas, Projeção de Bonus, Carreira Atual, Pontos Projetados, Pontos Consolidados, Saldo Disponível, Documentação
            {'key': 'network', 'title': 'Rede', 'value': team_size, 'icon': 'Users', 'delta': f"Diretos: {directs_count}"},
            {'key': 'sold_plants', 'title': 'Usinas Vendidas', 'value': sold_plants_count, 'icon': 'Factory', 'delta': None},
            {'key': 'bonus_projection', 'title': 'Projeção de Bônus', 'value': bonus_projection_value, 'icon': 'DollarSign', 'delta': f"mês {month_label}"},
            {'key': 'career', 'title': 'Carreira Atual', 'value': (current_licensed.current_career.stage_name if current_licensed.current_career else '-'), 'icon': 'Shield', 'delta': None},
            {'key': 'points_projected', 'title': 'Pontos Projetados', 'value': points_projected, 'icon': 'Target', 'delta': None},
            {'key': 'points_consolidated', 'title': 'Pontos Consolidados', 'value': points_consolidated, 'icon': 'CheckCircle', 'delta': None},
            {'key': 'balance_available', 'title': 'Saldo Disponível', 'value': balance_available, 'icon': 'DollarSign', 'delta': 'consolidado'},
            {'key': 'docs_status', 'title': 'Documentação', 'value': docs_map, 'icon': 'File', 'delta': None},
        ]

        data['quickActions'] = [
            {'label': 'Cadastrar Licenciado', 'route': '/preRegister'},
            {'label': 'Árvore da Rede', 'route': '/network/tree'},
            {'label': 'Enviar Documentos', 'route': '/documents'},
        ]

        # Banner de documentos — incluir PF/PJ detalhado e CNPJs de empresas
        try:
            from core.models.LicensedCompany import LicensedCompany as _LC
            import re as _re
            company_cnpjs = [
                _re.sub(r'\D', '', str(c.cnpj or ''))
                for c in _LC.objects.filter(licensed=current_licensed).only('cnpj')
            ]
        except Exception:
            company_cnpjs = []
        data['documents'] = {
            'status': current_licensed.stt_document,
            'pending': (docs_map.get('pf') != 'approved') or (company_cnpjs and docs_map.get('pj') != 'approved'),
            'pf': docs_map.get('pf'),
            'pj': docs_map.get('pj'),
            'company_cnpjs': company_cnpjs,
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

        # Detalhes de assinatura/plano (lista para o dashboard do licenciado)
        try:
            plan_name = getattr(getattr(current_licensed, 'plan', None), 'name', None)
            dtt_cadastro = getattr(current_licensed, 'dtt_record', None)
            dtt_ativacao = getattr(current_licensed, 'dtt_activation', None)

            expires_at = None
            contract_status_raw = None
            contract_status = 'pending'

            if last_adesion:
                contract_status_raw = getattr(last_adesion, 'contract_status', None)
                # Expiração: 12 meses após pagamento confirmado
                if getattr(last_adesion, 'ind_payment_status', None) == 'confirmed' and getattr(last_adesion, 'dtt_payment', None):
                    try:
                        expires_at = last_adesion.dtt_payment + timezone.timedelta(days=365)
                    except Exception:
                        expires_at = None
                # Normaliza status de contrato em "signed" | "pending"
                cs = str(contract_status_raw or '').strip().lower()
                if cs in {'signed', 'approved', 'assinado', 'ativo', 'active'}:
                    contract_status = 'signed'
                else:
                    contract_status = 'pending'

            data['subscription'] = {
                'plan_name': plan_name,
                'dtt_record': dtt_cadastro.isoformat() if dtt_cadastro else None,
                'dtt_activation': dtt_ativacao.isoformat() if dtt_ativacao else None,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'contract_status': contract_status,
                'contract_status_raw': contract_status_raw,
            }
        except Exception:
            data['subscription'] = {
                'plan_name': None,
                'dtt_record': None,
                'dtt_activation': None,
                'expires_at': None,
                'contract_status': 'pending',
                'contract_status_raw': None,
            }

        return Response(data)


class AdminSchedulesView(APIView):
    """Exibe configurações de rotinas agendadas (Celery Beat) para admins.

    Retorna lista com: nome, descrição, schedule (crontab/human readable), próxima execução estimada e task.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_operator_or_admin = user.is_superuser or user.is_staff or user.groups.filter(name='Operador').exists()
        if not is_operator_or_admin:
            return Response([], status=403)

        from django.conf import settings
        schedules = []
        beat = getattr(settings, 'CELERY_BEAT_SCHEDULE', {}) or {}

        now = dj_tz.localtime()

        for key, item in beat.items():
            task = item.get('task')
            schedule = item.get('schedule')
            description = item.get('description') or ''
            human = None
            next_run = None

            # CrontabSchedule do celery possui método remaining_estimate; estimamos próxima execução
            try:
                if isinstance(schedule, crontab):
                    human = f"crontab(min={schedule._orig_minute}, hour={schedule._orig_hour}, day_of_month={schedule._orig_day_of_month}, month={schedule._orig_month_of_year}, day_of_week={schedule._orig_day_of_week})"
                    # próxima execução baseada no método de remanescente
                    delta = schedule.remaining_estimate(now)
                    next_run = (now + delta).isoformat()
                else:
                    # intervalos ou outros tipos – tentativa genérica
                    human = str(schedule)
                    try:
                        delta = schedule.remaining_estimate(now)
                        next_run = (now + delta).isoformat()
                    except Exception:
                        next_run = None
            except Exception:
                human = str(schedule)
                next_run = None

            schedules.append({
                'key': key,
                'task': task,
                'description': description,
                'schedule': human,
                'next_run': next_run,
            })

        return Response({'generated_at': now.isoformat(), 'entries': schedules})

    def post(self, request):
        """Ações de administração: toggle ativa/inativa (com motivo) e executar agora.

        Body:
        - action: 'toggle' | 'run_now'
        - key: chave do CELERY_BEAT_SCHEDULE
        - active: bool (para toggle)
        - reason: texto (obrigatório quando active=false)
        """
        user = request.user
        is_operator_or_admin = user.is_superuser or user.is_staff or user.groups.filter(name='Operador').exists()
        if not is_operator_or_admin:
            return Response({'detail': 'Sem permissão'}, status=403)

        action = (request.data.get('action') or '').strip()
        key = (request.data.get('key') or '').strip()
        if not key:
            return Response({'key': 'Informe a chave da rotina.'}, status=400)

        beat = getattr(settings, 'CELERY_BEAT_SCHEDULE', {}) or {}
        if key not in beat:
            return Response({'key': 'Rotina não encontrada.'}, status=404)

        # Garante registro de config
        item = beat[key]
        cfg, _ = ScheduledTaskConfig.objects.get_or_create(key=key, defaults={'task': item.get('task') or ''})

        if action == 'toggle':
            if 'active' not in request.data:
                return Response({'active': 'Informe active=true/false.'}, status=400)
            active = bool(request.data.get('active'))
            reason = (request.data.get('reason') or '').strip() or None
            if not active and not reason:
                return Response({'reason': 'Informe o motivo da desativação.'}, status=400)
            cfg.active = active
            cfg.disabled_reason = None if active else reason
            cfg.task = item.get('task') or cfg.task
            cfg.save()
            ScheduledTaskLog.objects.create(config=cfg, action=('enable' if active else 'disable'), actor_username=user.username, reason=reason)
            ser = ScheduledTaskConfigSerializer(cfg)
            return Response({'ok': True, 'config': ser.data})

        if action == 'run_now':
            # opcionalmente checa active
            if cfg.active is False:
                ScheduledTaskLog.objects.create(config=cfg, action='run_now', actor_username=user.username, reason='Executado manualmente (mesmo desativado)')
            else:
                ScheduledTaskLog.objects.create(config=cfg, action='run_now', actor_username=user.username, reason='Executado manualmente')
            # Disparo da task
            try:
                from celery import current_app
                task_name = item.get('task')
                current_app.send_task(task_name)
                return Response({'ok': True, 'message': f'Task {task_name} enfileirada para execução imediata.'})
            except Exception as e:
                return Response({'ok': False, 'error': str(e)}, status=500)

        return Response({'action': 'Use action=toggle ou action=run_now'}, status=400)


class PendingDocumentsCountView(APIView):
    """
    Endpoint para contar documentos pendentes de revisão (apenas para operadores)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
        
        if not is_operator:
            return Response({'count': 0, 'message': 'Acesso negado'}, status=403)
        
        # Contar documentos com status 'pending'
        count = LicensedDocument.objects.filter(stt_validate='pending').count()
        
        return Response({'count': count})


class CareerDataView(APIView):
    """
    Endpoint para buscar dados de carreira do usuário atual
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            # Buscar licenciado atual
            licensed = Licensed.objects.select_related('current_career').get(user=user)
            
            # Inicializar dados com valores padrão
            career_data = {
                'stats': {
                    'sales': 0,
                    'referrals': 0,
                    'commissions': 0.0,
                    'ranking': 1
                },
                'current_level': 'Bronze',
                'career_plans': []
            }
            
            # Buscar planos de carreira ordenados por pontos
            try:
                from plans.models.PlanCareer import PlanCareer
                career_plans = PlanCareer.objects.filter(stt_record=True).order_by('required_points')
                print(f"DEBUG: Encontrados {career_plans.count()} planos de carreira")
                
                # Processar planos de carreira
                for plan in career_plans:
                    career_data['career_plans'].append({
                        'id': plan.id,
                        'stage_name': plan.stage_name,
                        'reward_description': plan.reward_description,
                        'required_points': plan.required_points,
                        'required_directs': plan.required_directs,
                        'required_direct_sales': plan.required_direct_sales,
                        'progress': 0.0,
                        'is_current': plan == licensed.current_career,
                        'cover_image': plan.cover_image.url if plan.cover_image else None
                    })
                
                # Definir nível atual
                if licensed.current_career:
                    career_data['current_level'] = licensed.current_career.stage_name
                    print(f"DEBUG: Carreira atual: {licensed.current_career.stage_name}")
                else:
                    print("DEBUG: Licenciado não possui carreira atual definida")
                    
            except Exception as e:
                print(f"Erro ao carregar planos de carreira: {e}")
                import traceback
                traceback.print_exc()
            
            # Calcular estatísticas do usuário (com fallbacks)
            try:
                from contractor.models import Proposal
                sales_count = Proposal.objects.filter(
                    contractor__licensed=licensed,
                    status='Aprovado'
                ).count()
                career_data['stats']['sales'] = sales_count
            except Exception as e:
                print(f"Erro ao calcular vendas: {e}")
            
            try:
                direct_referrals = Licensed.objects.filter(
                    user__groups__name='Licenciado',
                    original_indicator=licensed
                ).count()
                career_data['stats']['referrals'] = direct_referrals
            except Exception as e:
                print(f"Erro ao calcular indicações: {e}")
            
            try:
                from network.models.ScoreReference import ScoreReference
                total_points = ScoreReference.objects.filter(
                    receiver_licensed=licensed,
                    status='valid'
                ).aggregate(total=Sum('points_amount'))['total'] or 0
                career_data['stats']['commissions'] = float(total_points * 0.1)
            except Exception as e:
                print(f"Erro ao calcular comissões: {e}")
            
            # Recalcular progresso dos planos com os dados reais
            sales_count = career_data['stats']['sales']
            direct_referrals = career_data['stats']['referrals']
            
            for plan_data in career_data['career_plans']:
                sales_progress = min((sales_count / plan_data['required_direct_sales']) * 100, 100) if plan_data['required_direct_sales'] > 0 else 100
                referrals_progress = min((direct_referrals / plan_data['required_directs']) * 100, 100) if plan_data['required_directs'] > 0 else 100
                plan_data['progress'] = round((sales_progress + referrals_progress) / 2, 1)
            
            print(f"DEBUG: Retornando dados de carreira: {career_data}")
            return Response(career_data)
            
        except Licensed.DoesNotExist:
            return Response({'error': 'Usuário não possui perfil de licenciado'}, status=404)
        except Exception as e:
            print(f"Erro geral na API de carreira: {e}")
            return Response({'error': f'Erro interno: {str(e)}'}, status=500)


class GeneralReportView(APIView):
    """
    Endpoint para buscar dados do relatório geral da plataforma
    
    Este endpoint fornece estatísticas completas sobre:
    - Faturamento total e crescimento
    - Comissões pagas e crescimento
    - Afiliados ativos e crescimento
    - Novos cadastros e crescimento
    - Desempenho mensal (últimos 4 meses)
    - Top afiliados por performance
    
    Acesso: Apenas operadores e superadmins
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retorna dados do relatório geral
        
        Returns:
            Response: JSON com estatísticas e dados detalhados
        """
        user = request.user
        
        try:
            # ========================================
            # VERIFICAÇÃO DE PERMISSÕES
            # ========================================
            # Verificar se é operador ou superadmin
            is_operator = user.groups.filter(name='Operador').exists() or user.is_staff or user.is_superuser
            
            if not is_operator:
                return Response({'error': 'Acesso negado'}, status=403)
            
            # ========================================
            # CONFIGURAÇÃO DE DATAS
            # ========================================
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Calcular períodos para comparação
            now = timezone.now()
            current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month = (current_month - timedelta(days=1)).replace(day=1)
            
            # ========================================
            # INICIALIZAÇÃO DOS DADOS
            # ========================================
            # Estrutura base do relatório
            report_data = {
                'stats': {
                    'totalRevenue': 0.0,           # Faturamento total atual
                    'revenueGrowth': 0.0,          # Crescimento do faturamento (%)
                    'commissionsPaid': 0.0,        # Comissões pagas no período
                    'commissionsGrowth': 0.0,      # Crescimento das comissões (%)
                    'activeAffiliates': 0,         # Número de afiliados ativos
                    'affiliatesGrowth': 0.0,       # Crescimento de afiliados (%)
                    'newRegistrations': 0,         # Novos cadastros no período
                    'registrationsGrowth': 0.0     # Crescimento de cadastros (%)
                },
                'monthly_performance': [],         # Desempenho dos últimos 4 meses
                'top_affiliates': []               # Top 4 afiliados por performance
            }
            
            # ========================================
            # CÁLCULO DO FATURAMENTO TOTAL
            # ========================================
            # Baseado nos planos de adesão pagos
            try:
                from plans.models.PlanAdesion import PlanAdesion
                
                # Faturamento do mês atual
                current_revenue = PlanAdesion.objects.filter(
                    dtt_payment__gte=current_month,
                    dtt_payment__lt=current_month + timedelta(days=32)
                ).aggregate(total=Sum('plan__price'))['total'] or 0
                
                # Faturamento do mês passado (para comparação)
                last_revenue = PlanAdesion.objects.filter(
                    dtt_payment__gte=last_month,
                    dtt_payment__lt=current_month
                ).aggregate(total=Sum('plan__price'))['total'] or 0
                
                # Atualizar dados do relatório
                report_data['stats']['totalRevenue'] = float(current_revenue)
                if last_revenue > 0:
                    report_data['stats']['revenueGrowth'] = round(((current_revenue - last_revenue) / last_revenue) * 100, 1)
                    
            except Exception as e:
                print(f"Erro ao calcular faturamento: {e}")
            
            # ========================================
            # CÁLCULO DAS COMISSÕES PAGAS
            # ========================================
            # Baseado nos pontos gerados (ScoreReference)
            try:
                from network.models.ScoreReference import ScoreReference
                
                # Pontos gerados no mês atual
                current_commissions = ScoreReference.objects.filter(
                    dtt_record__gte=current_month,
                    dtt_record__lt=current_month + timedelta(days=32),
                    stt_record=True
                ).aggregate(total=Sum('points_amount'))['total'] or 0
                
                # Pontos gerados no mês passado (para comparação)
                last_commissions = ScoreReference.objects.filter(
                    dtt_record__gte=last_month,
                    dtt_record__lt=current_month,
                    stt_record=True
                ).aggregate(total=Sum('points_amount'))['total'] or 0
                
                # Converter pontos para valor monetário (R$ 0,10 por ponto)
                report_data['stats']['commissionsPaid'] = float(current_commissions * 0.1)
                if last_commissions > 0:
                    report_data['stats']['commissionsGrowth'] = round(((current_commissions - last_commissions) / last_commissions) * 100, 1)
                    
            except Exception as e:
                print(f"Erro ao calcular comissões: {e}")
            
            # ========================================
            # CÁLCULO DE AFILIADOS ATIVOS
            # ========================================
            # Afiliados com pagamento em dia (último ano)
            try:
                # Afiliados ativos atuais (com pagamento no último ano)
                current_affiliates = Licensed.objects.filter(
                    stt_record=True,
                    dtt_payment_received__gte=current_month - timedelta(days=365)
                ).count()
                
                # Afiliados ativos no mês passado (para comparação)
                last_affiliates = Licensed.objects.filter(
                    stt_record=True,
                    dtt_payment_received__gte=last_month - timedelta(days=365),
                    dtt_payment_received__lt=current_month - timedelta(days=365)
                ).count()
                
                # Atualizar dados do relatório
                report_data['stats']['activeAffiliates'] = current_affiliates
                if last_affiliates > 0:
                    report_data['stats']['affiliatesGrowth'] = round(((current_affiliates - last_affiliates) / last_affiliates) * 100, 1)
                    
            except Exception as e:
                print(f"Erro ao calcular afiliados: {e}")
            
            # ========================================
            # CÁLCULO DE NOVOS CADASTROS
            # ========================================
            # Novos licenciados cadastrados no período
            try:
                # Cadastros do mês atual
                current_registrations = Licensed.objects.filter(
                    dtt_record__gte=current_month,
                    dtt_record__lt=current_month + timedelta(days=32)
                ).count()
                
                # Cadastros do mês passado (para comparação)
                last_registrations = Licensed.objects.filter(
                    dtt_record__gte=last_month,
                    dtt_record__lt=current_month
                ).count()
                
                # Atualizar dados do relatório
                report_data['stats']['newRegistrations'] = current_registrations
                if last_registrations > 0:
                    report_data['stats']['registrationsGrowth'] = round(((current_registrations - last_registrations) / last_registrations) * 100, 1)
                    
            except Exception as e:
                print(f"Erro ao calcular cadastros: {e}")
            
            # ========================================
            # DESEMPENHO MENSAL (ÚLTIMOS 4 MESES)
            # ========================================
            # Histórico de performance para análise de tendências
            try:
                months = []
                for i in range(4):
                    # Calcular período do mês (i meses atrás)
                    month_start = current_month - timedelta(days=30*i)
                    month_end = month_start + timedelta(days=32)
                    
                    # Faturamento do mês
                    month_revenue = PlanAdesion.objects.filter(
                        dtt_payment__gte=month_start,
                        dtt_payment__lt=month_end
                    ).aggregate(total=Sum('plan__price'))['total'] or 0
                    
                    # Comissões do mês (pontos convertidos)
                    month_commissions = ScoreReference.objects.filter(
                        dtt_record__gte=month_start,
                        dtt_record__lt=month_end,
                        stt_record=True
                    ).aggregate(total=Sum('points_amount'))['total'] or 0
                    
                    # Novos afiliados do mês
                    month_affiliates = Licensed.objects.filter(
                        dtt_record__gte=month_start,
                        dtt_record__lt=month_end
                    ).count()
                    
                    # Adicionar dados do mês
                    months.append({
                        'month': month_start.strftime('%B'),
                        'revenue': float(month_revenue),
                        'commissions': float(month_commissions * 0.1),
                        'affiliates': month_affiliates
                    })
                
                # Ordenar do mais antigo para o mais recente
                report_data['monthly_performance'] = list(reversed(months))
                
            except Exception as e:
                print(f"Erro ao calcular desempenho mensal: {e}")
            
            # ========================================
            # TOP AFILIADOS (BASEADO EM VENDAS)
            # ========================================
            # Ranking dos melhores performadores
            try:
                from contractor.models import Proposal
                
                top_affiliates_data = []
                # Buscar top 4 afiliados por número de vendas
                top_licensed = Licensed.objects.filter(
                    stt_record=True
                ).annotate(
                    sales_count=models.Count('contractors__proposals', filter=models.Q(contractors__proposals__status='Aprovado'))
                ).order_by('-sales_count')[:4]
                
                # Processar cada afiliado
                for licensed in top_licensed:
                    # Contar vendas aprovadas
                    sales_count = Proposal.objects.filter(
                        contractor__licensed=licensed,
                        status='Aprovado'
                    ).count()
                    
                    # Calcular comissão estimada (R$ 1000 por venda)
                    commission = sales_count * 1000
                    
                    # Adicionar ao ranking
                    top_affiliates_data.append({
                        'name': licensed.user.get_full_name() or licensed.user.username,
                        'sales': sales_count,
                        'commission': float(commission),
                        'level': licensed.current_career.stage_name if licensed.current_career else 'Bronze'
                    })
                
                report_data['top_affiliates'] = top_affiliates_data
                
            except Exception as e:
                print(f"Erro ao calcular top afiliados: {e}")
            
            # ========================================
            # RETORNO DOS DADOS
            # ========================================
            return Response(report_data)
            
        except Exception as e:
            print(f"Erro geral na API de relatório: {e}")
            return Response({'error': f'Erro interno: {str(e)}'}, status=500)


class VerifyCareerView(APIView):
    """
    Verifica a pontuação e diretos do licenciado atual e atualiza a carreira conforme
    a configuração de planos de carreira (PlanCareer).
    Regras básicas:
      - Seleciona o maior plano cujo required_points e required_directs foram atendidos.
      - Pontos: soma de ScoreReference.valid para o licenciado.
      - Diretos: quantidade de licenciados com original_indicator = licenciado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from plans.models.PlanCareer import PlanCareer
            from network.models.ScoreReference import ScoreReference
            from contractor.models import Proposal
            current_licensed = Licensed.objects.select_related('user', 'current_career').get(user=request.user)

            # Métricas atuais
            total_points = (
                ScoreReference.objects
                .filter(receiver_licensed=current_licensed, status='valid')
                .aggregate(total=Sum('points_amount'))['total'] or 0
            )
            directs = Licensed.objects.filter(original_indicator=current_licensed).count()
            sales_count = Proposal.objects.filter(contractor__licensed=current_licensed, status='Aprovado').count()

            # Escolhe o melhor plano atingido
            careers = (
                PlanCareer.objects
                .filter(stt_record=True)
                .order_by('required_points', 'required_directs')
            )
            best = None
            for c in careers:
                if (
                    total_points >= (getattr(c, 'required_points', 0) or 0)
                    and directs >= (getattr(c, 'required_directs', 0) or 0)
                    and sales_count >= (getattr(c, 'required_direct_sales', 0) or 0)
                ):
                    best = c
            # Próximo alvo (primeiro plano acima do best que ainda não atingiu)
            next_plan = None
            for c in careers:
                if best is None:
                    # Primeiro plano da lista que não atingiu
                    if not (
                        total_points >= (getattr(c, 'required_points', 0) or 0)
                        and directs >= (getattr(c, 'required_directs', 0) or 0)
                        and sales_count >= (getattr(c, 'required_direct_sales', 0) or 0)
                    ):
                        next_plan = c
                        break
                else:
                    if (
                        (getattr(c, 'required_points', 0) or 0) > (getattr(best, 'required_points', 0) or 0)
                        or (getattr(c, 'required_directs', 0) or 0) > (getattr(best, 'required_directs', 0) or 0)
                        or (getattr(c, 'required_direct_sales', 0) or 0) > (getattr(best, 'required_direct_sales', 0) or 0)
                    ):
                        # c é acima de best
                        if not (
                            total_points >= (getattr(c, 'required_points', 0) or 0)
                            and directs >= (getattr(c, 'required_directs', 0) or 0)
                            and sales_count >= (getattr(c, 'required_direct_sales', 0) or 0)
                        ):
                            next_plan = c
                            break
            # Guarda nome ANTES
            before_name = getattr(getattr(current_licensed, 'current_career', None), 'stage_name', None)
            with transaction.atomic():
                if best and current_licensed.current_career_id != getattr(best, 'id', None):
                    current_licensed.current_career = best
                    current_licensed.save(update_fields=['current_career'])

            updated = bool(best and current_licensed.current_career_id == getattr(best, 'id', None))
            # Ajuste: if updated just happened, before is previous; mas não temos previous; retornamos 'before' via payload best BEFORE change. Para simplificar, expor both names.
            after_name = getattr(getattr(current_licensed, 'current_career', None), 'stage_name', None)
            best_name = getattr(best, 'stage_name', None)
            # Missing to next plan
            missing_points = None
            missing_directs = None
            missing_sales = None
            if next_plan is not None:
                rp = getattr(next_plan, 'required_points', 0) or 0
                rd = getattr(next_plan, 'required_directs', 0) or 0
                rs = getattr(next_plan, 'required_direct_sales', 0) or 0
                missing_points = max(0, rp - (total_points or 0))
                missing_directs = max(0, rd - (directs or 0))
                missing_sales = max(0, rs - (sales_count or 0))

            return Response({
                'updated': updated,
                'before': before_name,
                'after': after_name,
                'metrics': {
                    'points': float(total_points),
                    'directs': directs,
                    'sales': sales_count,
                },
                'next': {
                    'stage_name': getattr(next_plan, 'stage_name', None),
                    'required_points': getattr(next_plan, 'required_points', None),
                    'required_directs': getattr(next_plan, 'required_directs', None),
                    'required_direct_sales': getattr(next_plan, 'required_direct_sales', None),
                } if next_plan else None,
                'missing': {
                    'points': missing_points,
                    'directs': missing_directs,
                    'sales': missing_sales,
                } if next_plan is not None else None,
            })
        except Licensed.DoesNotExist:
            return Response({'error': 'Usuário não possui perfil de licenciado'}, status=404)
        except Exception as e:
            return Response({'error': f'Erro ao verificar carreira: {str(e)}'}, status=500)
