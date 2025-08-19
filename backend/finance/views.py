from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models.GatewayConfig import GatewayConfig
from .models.Transaction import Transaction
from .models.PaymentLink import PaymentLink
from .serializers import GatewayConfigSerializer, TransactionSerializer, PaymentLinkSerializer


class GatewayConfigViewSet(viewsets.ModelViewSet):
    queryset = GatewayConfig.objects.all()
    serializer_class = GatewayConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        instance = GatewayConfig.objects.first()
        if not instance:
            # Garante um registro default para a UI preencher
            instance = GatewayConfig.objects.create(
                name='Pagarme',
                api_token='',
                api_url='https://sdx-api.pagar.me/core/v5/paymentlinks',
                active=True,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related('virtual_account__licensed__user').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

class PaymentLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentLink.objects.select_related('licensed', 'adesion').all()
    serializer_class = PaymentLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        adesion_id = self.request.query_params.get('adesion')
        if adesion_id:
            qs = qs.filter(adesion_id=adesion_id)
        return qs

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class PaymentLinkLatestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        adesion_id = request.query_params.get('adesion')
        licensed_username = request.query_params.get('licensed_username')
        qs = PaymentLink.objects.all()
        if adesion_id:
            qs = qs.filter(adesion_id=adesion_id)
        elif licensed_username:
            qs = qs.filter(licensed__user__username__iexact=licensed_username)
        else:
            return Response({'detail': 'informe adesion ou licensed_username'}, status=400)
        qs = qs.order_by('-created_at')
        obj = qs.first()
        if not obj:
            return Response(None, status=204)
        serializer = PaymentLinkSerializer(obj)
        return Response(serializer.data)

