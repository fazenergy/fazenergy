from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectsTreeView, ScoreReferenceViewSet, BonusReferenceViewSet

router = DefaultRouter()
router.register(r'score-references', ScoreReferenceViewSet, basename='score-references')
router.register(r'bonus-references', BonusReferenceViewSet, basename='bonus-references')

urlpatterns = [
    path('tree/', DirectsTreeView.as_view(), name='network-tree'),
    path('', include(router.urls)),
]







