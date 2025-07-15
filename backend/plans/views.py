# plans/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Plan
from .serializers import PlanSerializer
from .models import PlanAdesion
from .serializers import PlanAdesionSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]  # ✅ Protege rota

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