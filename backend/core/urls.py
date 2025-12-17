# ========================================
# IMPORTAÇÕES
# ========================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar todas as views do módulo core
from .views import (
    LicensedViewSet,              # CRUD de licenciados
    UserProfileView,              # Perfil do usuário
    validate_referrer,            # Validação de indicador
    LicensedPreRegisterView,      # Pré-cadastro de licenciados
    DirectLicensedListView,       # Lista de diretos
    DownlineTreeListView,         # Árvore de downlines
    DashboardView,                # Dados do dashboard
    LicensedDocumentViewSet,      # CRUD de documentos
    LicensedCompanyViewSet,       # CRUD de empresas do licenciado
    LicensedLookupView,           # Busca de licenciados
    AdminUserViewSet,             # CRUD de usuários (admin)
    AdminGroupViewSet,            # CRUD de grupos (admin)
    AdminPermissionViewSet,       # CRUD de permissões (admin)
    PendingDocumentsCountView,    # Contagem de documentos pendentes
    CareerDataView,               # Dados de carreira do usuário
    GeneralReportView,            # Relatório geral da plataforma
    CurrentLicensedView,          # Licensed do usuário atual
    VerifyCareerView,             # Verificar/atualizar carreira
    AdminSchedulesView,           # Dashboard de rotinas agendadas
)

# ========================================
# CONFIGURAÇÃO DO ROUTER
# ========================================
# Router para ViewSets (CRUD automático)
router = DefaultRouter()
router.register(r'licensed', LicensedViewSet)                                    # /api/core/licensed/
router.register(r'licensed-documents', LicensedDocumentViewSet, basename='licensed-documents')  # /api/core/licensed-documents/
router.register(r'licensed-companies', LicensedCompanyViewSet, basename='licensed-companies')  # /api/core/licensed-companies/
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')       # /api/core/admin/users/
router.register(r'admin/groups', AdminGroupViewSet, basename='admin-groups')    # /api/core/admin/groups/
router.register(r'admin/permissions', AdminPermissionViewSet, basename='admin-permissions')  # /api/core/admin/permissions/

# ========================================
# URL PATTERNS
# ========================================
# URLs customizadas (APIViews)
urlpatterns = [
    # URLs do router (ViewSets)
    path('', include(router.urls)),
    
    # URLs customizadas (APIViews)
    path('profile/', UserProfileView.as_view(), name='profile'),                    # Perfil do usuário
    path('profile/licensed/', CurrentLicensedView.as_view(), name='profile-licensed'),  # Licensed do usuário atual
    path('validate-referrer/<str:username>/', validate_referrer, name='validate-referrer'),  # Validação de indicador
    path('pre-register/', LicensedPreRegisterView.as_view(), name='pre-register'),      # Pré-cadastro
    path('directs/', DirectLicensedListView.as_view(), name='licensed-directs'),        # Lista de diretos
    path('downlines/', DownlineTreeListView.as_view(), name='licensed-downlines'),      # Árvore de downlines
    path('dashboard/', DashboardView.as_view(), name='dashboard-data'),                 # Dados do dashboard
    path('lookup/licensed/', LicensedLookupView.as_view(), name='lookup-licensed'),     # Busca de licenciados
    path('pending-documents-count/', PendingDocumentsCountView.as_view(), name='pending-documents-count'),  # Contagem de documentos
    path('career-data/', CareerDataView.as_view(), name='career-data'),                 # Dados de carreira
    path('career/verify/', VerifyCareerView.as_view(), name='career-verify'),           # Verificar carreira atual
    path('general-report/', GeneralReportView.as_view(), name='general-report'),        # Relatório geral
    path('admin/schedules/', AdminSchedulesView.as_view(), name='admin-schedules'),     # Rotinas agendadas (admin)
]