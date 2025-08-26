from rest_framework import viewsets
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


class ProposalResultViewSet(viewsets.ModelViewSet):
    queryset = ProposalResult.objects.all()
    serializer_class = ProposalResultSerializer
    permission_classes = [IsAuthenticated]


