from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models.NotifyConfig import NotifyConfig
from .models.NotifyTemplate import NotifyTemplate
from .serializers import NotifyConfigSerializer, NotifyTemplateSerializer
from .utils import send_email


class NotifyConfigViewSet(viewsets.ModelViewSet):
    queryset = NotifyConfig.objects.all()
    serializer_class = NotifyConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        instance = NotifyConfig.objects.first()
        if not instance:
            return Response(None)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NotifyTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotifyTemplate.objects.all().order_by('id')
    serializer_class = NotifyTemplateSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='test')
    def test_send(self, request, pk=None):
        template = self.get_object()
        config = NotifyConfig.objects.first()
        to = request.data.get('to') or (config.test_recipient if config else None)
        if not to:
            return Response({'detail': 'Destinatário de teste não configurado.'}, status=status.HTTP_400_BAD_REQUEST)
        context = { 'nome': 'Teste', 'id': 'USR001', 'nova_senha': 'abc123', 'site_url': 'https://faz.energy' }
        try:
            send_email(template.name, context, [to])
            return Response({'detail': f'Email de teste enviado para {to}'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render

# Create your views here.
