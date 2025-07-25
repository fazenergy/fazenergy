from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models.user_manager import Affiliate, User
from .serializers import AffiliateSerializer, UserProfileSerializer

class AffiliateViewSet(viewsets.ModelViewSet):
    queryset = Affiliate.objects.all()
    serializer_class = AffiliateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
