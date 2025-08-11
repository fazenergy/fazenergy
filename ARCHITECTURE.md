# Arquitetura - FazEnergyFinal

## Visão Geral
- Monorepo com `@backend/` (Django + DRF) e `@frontend/` (Vue 3 + Vite).
- Comunicação via API REST JSON.
- Orquestração via Docker Compose (banco PostgreSQL, backend, frontend).

## Serviços (docker-compose)
- Banco: `postgres:15` exposto em `5432`.
- Backend: Django em `8000` (container `fazenergy-backend`).
- Frontend: Vite Dev Server em `5173` (container `fazenergy-frontend`).

## Backend (`@backend/`)
- Stack: Django 5, DRF, SimpleJWT, Celery, Redis (para filas), PostgreSQL.
- Admin: Jazzmin.
- Apps modulares (exemplos): `core`, `proposal`, `plans`, `contracts`, `finance`, `network`, `location`, `notifications`, `webhooks`.
- Arquivos relevantes:
  - `config/settings.py`, `config/urls.py`, `config/celery.py`.
- Uploads/estática: `MEDIA_URL`/`MEDIA_ROOT` e `static/`.

Rotas base (sujeitas a evoluções; conferir no código):
```9:27:backend/config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('core.urls')),
    path('api/core/', include('core.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('core.urls')),  # ou o nome do seu app
    path('api/location/', include('location.urls')),
    path('api/proposal/', include('proposal.urls')),    

    # Webhooks
    path('api/webhook/pagarme/', pagarme_webhook, name='webhook-pagarme'),
    #path('api/webhook/lexio/', lexio_webhook, name='webhook-lexio'),
    #path('api/webhook/lexio', lexio_webhook),  # para aceitar sem a barra também

    # Importante para Upload
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    
   


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Frontend (`@frontend/`)
- Stack: Vue 3, Vite, Tailwind CSS, Pinia, Vue Router, Axios.
- Estrutura:
  - `src/views` (páginas), `src/components` (componentes), `src/services` (APIs), `src/store` (estado), `src/router` (rotas), `src/config` (configs).
- Dev server: `http://localhost:5173`.

## Como rodar (Docker)
1) Configure `.env` na raiz com:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

2) Suba os serviços:
```bash
docker compose up -d --build
```

- Backend: `http://localhost:8000/`
- Frontend: `http://localhost:5173/`

## Diretrizes de Evolução
- Tratar apps Django como modulares e evolutivos (novos apps/rotas podem surgir).
- Documentar rotas/fluxos mais detalhados aqui conforme evoluem (evitar duplicar regra de negócio).
- Manter `.cursorrules` estável ao nível conceitual e referenciar este documento para detalhes vivos.

