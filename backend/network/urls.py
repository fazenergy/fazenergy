from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectsTreeView, ScoreReferenceViewSet

router = DefaultRouter()
router.register(r'score-references', ScoreReferenceViewSet, basename='score-references')

urlpatterns = [
    path('tree/', DirectsTreeView.as_view(), name='network-tree'),
    path('', include(router.urls)),
]







