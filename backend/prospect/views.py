from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Prospect, Proposal, ProposalResult
from .serializers import ProspectSerializer, ProposalSerializer, ProposalResultSerializer


class ProspectViewSet(viewsets.ModelViewSet):
    queryset = Prospect.objects.all()
    serializer_class = ProspectSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]


class ProposalResultViewSet(viewsets.ModelViewSet):
    queryset = ProposalResult.objects.all()
    serializer_class = ProposalResultSerializer
    permission_classes = [IsAuthenticated]
