from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
        """Retorna todos diretos e indiretos do licenciado logado (ou de um target, se operador/superadmin), com níveis."""
        user = request.user
        from core.models.Licensed import Licensed
        try:
            current_licensed = Licensed.objects.select_related('user').get(user=user)
        except Licensed.DoesNotExist:
            return Response([], status=200)

        target = current_licensed
        # Operador ou superadmin podem inspecionar outro usuário por query param
        if getattr(user, 'is_superuser', False) or user.groups.filter(name__in=['Operador']).exists():
            q = request.query_params.get('target')
            if q:
                target = Licensed.objects.filter(user__username__iexact=q).first() or target

        # BFS por 5 níveis
        levels = {}
        uplines = {}
        collected_ids = set()
        frontier = [target]
        for lvl in range(1, 6):
            rels = (
                UnilevelNetwork.objects
                .filter(upline_licensed__in=frontier, level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )
            next_frontier = []
            for r in rels:
                did = r.downline_licensed_id
                if did not in collected_ids:
                    levels[did] = lvl
                    uplines[did] = r.upline_licensed.user.username
                    collected_ids.add(did)
                    next_frontier.append(r.downline_licensed)
            if not next_frontier:
                break
            frontier = next_frontier

        qs = Licensed.objects.filter(id__in=collected_ids).select_related('user', 'plan', 'city_lookup')
        serializer = self.get_serializer(qs, many=True, context={'levels': levels, 'uplines': uplines})
        return Response(serializer.data)


@require_GET
@csrf_exempt
def validate_referrer(request, username):
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"valid": exists})
