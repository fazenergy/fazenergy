from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Contractor, Proposal, ProposalResult
from .serializers import ContractorSerializer, ProposalSerializer, ProposalResultSerializer


class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.select_related('contractor').all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='exists')
    def exists(self, request):
        """
        Verifica existência de proposta ativa (não expirada) para o par CPF/CNPJ + CEP.
        Parâmetros: zip_code (CEP, só números), cpf_cnpj (só números)
        Opcional: licensed_id (para retornar informação contextual)
        """
        zip_code = (request.query_params.get('zip_code') or '').strip()
        cpf_cnpj = (request.query_params.get('cpf_cnpj') or '').strip()

        # Normaliza apenas números
        import re
        zip_code = re.sub(r'\D', '', zip_code)
        cpf_cnpj = re.sub(r'\D', '', cpf_cnpj)

        if not zip_code or not cpf_cnpj:
            return Response({'detail': 'Parâmetros zip_code e cpf_cnpj são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Proposal.objects.filter(zip_code=zip_code, cpf_cnpj=cpf_cnpj, dtt_expired__isnull=True).select_related('contractor')
        exists = qs.exists()
        data = {
            'exists': exists,
            'count': qs.count(),
        }
        if exists:
            first = qs.first()
            data['licensed_id'] = getattr(getattr(first, 'contractor', None), 'licensed_id', None)
            data['proposal_id'] = first.id
            data['status'] = first.status
        return Response(data)


class ProposalResultViewSet(viewsets.ModelViewSet):
    queryset = ProposalResult.objects.all()
    serializer_class = ProposalResultSerializer
    permission_classes = [IsAuthenticated]


