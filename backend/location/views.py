from rest_framework import generics
from .models import State, City
from .serializers import StateSerializer, CitySerializer

class StateListView(generics.ListAPIView):
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer
    permission_classes = []  # Público

class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = []  # Público

    def get_queryset(self):
        state_id = self.request.query_params.get('state')
        qs = City.objects.all().order_by('name')
        if state_id:
            qs = qs.filter(state_id=state_id)
        return qs