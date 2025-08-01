from django.urls import path
from .views import StateListView, CityListView

urlpatterns = [
    path('states/', StateListView.as_view(), name='state-list'),
    path('cities/', CityListView.as_view(), name='city-list'),
]