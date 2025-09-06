from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LicensedViewSet,
    UserProfileView,
    validate_referrer,
    LicensedPreRegisterView,
    DirectLicensedListView,
    DownlineTreeListView,
    DashboardView,
    LicensedDocumentViewSet,
    LicensedLookupView,
    AdminUserViewSet,
    AdminGroupViewSet,
    AdminPermissionViewSet,
)

router = DefaultRouter()
router.register(r'licensed', LicensedViewSet)
router.register(r'licensed-documents', LicensedDocumentViewSet, basename='licensed-documents')
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')
router.register(r'admin/groups', AdminGroupViewSet, basename='admin-groups')
router.register(r'admin/permissions', AdminPermissionViewSet, basename='admin-permissions')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('validate-referrer/<str:username>/', validate_referrer, name='validate-referrer'),
    path('pre-register/', LicensedPreRegisterView.as_view(), name='pre-register'),
    path('directs/', DirectLicensedListView.as_view(), name='licensed-directs'),
    path('downlines/', DownlineTreeListView.as_view(), name='licensed-downlines'),
    path('dashboard/', DashboardView.as_view(), name='dashboard-data'),
    path('lookup/licensed/', LicensedLookupView.as_view(), name='lookup-licensed'),
]