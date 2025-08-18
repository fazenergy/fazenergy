from django.urls import path
from .views import DirectsTreeView

urlpatterns = [
    path('tree/', DirectsTreeView.as_view(), name='network-tree'),
]






