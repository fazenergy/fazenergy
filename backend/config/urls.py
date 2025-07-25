from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from webhooks.pagarme import pagarme_webhook
#from webhooks.lexio import lexio_webhook  # se tiver esse também

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/core/', include('core.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Webhooks
    path('api/webhook/pagarme/', pagarme_webhook, name='webhook-pagarme'),
    #path('api/webhook/lexio/', lexio_webhook, name='webhook-lexio'),
    #path('api/webhook/lexio', lexio_webhook),  # para aceitar sem a barra também

    # Importante para Upload
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    
   


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
