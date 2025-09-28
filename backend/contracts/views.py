from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ContractConfig, ContractTemplate
from .serializers import ContractConfigSerializer, ContractTemplateSerializer
from contracts.services import send_doc_adesion_to_lexio


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

    @action(detail=False, methods=['post'], url_path='resend-adesion')
    def resend_adesion(self, request):
        try:
            # Reenvia contrato para o licenciado logado
            from core.models.Licensed import Licensed
            lic = Licensed.objects.filter(user=request.user).first()
            if not lic:
                return Response({'error': 'Perfil de licenciado não encontrado'}, status=404)
            result = send_doc_adesion_to_lexio(lic.id)
            return Response({'ok': True, 'result': result})
        except Exception as e:
            return Response({'ok': False, 'error': str(e)}, status=400)


