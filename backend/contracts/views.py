from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ContractConfig, ContractTemplate
from .serializers import ContractConfigSerializer, ContractTemplateSerializer


class ContractConfigViewSet(viewsets.ModelViewSet):
    queryset = ContractConfig.objects.all()
    serializer_class = ContractConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        instance = ContractConfig.objects.first()
        if not instance:
            return Response(None)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ContractTemplateViewSet(viewsets.ModelViewSet):
    queryset = ContractTemplate.objects.all().order_by('id')
    serializer_class = ContractTemplateSerializer
    permission_classes = [IsAuthenticated]


