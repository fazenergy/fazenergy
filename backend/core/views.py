from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models.User import User
from .models.Licensed import Licensed
from .serializers import LicensedSerializer, UserProfileSerializer, LicensedListSerializer
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
        # Retorna os indicados diretos cujo indicador é o usuário logado
        return (
            Licensed.objects
            .filter(original_indicator__user=self.request.user)
            .select_related('user', 'plan', 'city_lookup', 'original_indicator')
            .order_by('-dtt_record')
        )


@require_GET
@csrf_exempt
def validate_referrer(request, username):
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"valid": exists})
