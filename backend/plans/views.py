from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models.Plan import Plan
from .serializers import PlanSerializer
from .models.PlanAdesion import PlanAdesion
from .serializers import PlanAdesionSerializer
from .models import Qualification
from .serializers import QualificationSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_permissions(self):
        if self.action == 'list':  # GET /api/plans/plans/
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class PlanAdesionViewSet(viewsets.ModelViewSet):
    queryset = PlanAdesion.objects.all()
    serializer_class = PlanAdesionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        serializer.save()


class QualificationViewSet(viewsets.ModelViewSet):
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context