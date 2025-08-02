# README.md

# FazEnergy

Ambiente de desenvolvimento local com Docker, Django (backend), Vue.js (frontend) e PostgreSQL.

---

## ?? Como rodar o projeto localmente

```bash
git clone <repo-url>
cd FazEnergy
cp .env.example .env
docker-compose up --build
```

- Backend Django: http://localhost:8000
- Frontend Vue.js: http://localhost:5173

### ?? Após subir os containers:

```bash
# Acessar o container do backend
docker exec -it fazenergy-backend-1 bash

# Rodar migrações do Django
python manage.py migrate

# Criar um superusuário
python manage.py createsuperuser

# (Opcional) Coletar arquivos estáticos
python manage.py collectstatic
```

---

## ?? Estrutura do Projeto

```
FazEnergy/
??? backend/             # Django Backend
?   ??? Dockerfile
??? frontend/            # Vue Frontend
?   ??? Dockerfile
??? docker-compose.yml   # Orquestra todos os serviços
??? .env                 # Variáveis de ambiente
??? .env.example         # Modelo de variáveis
```

---

## ?? Comandos úteis

```bash
# Acessar container do backend
docker exec -it fazenergy-backend-1 bash

# Rodar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

---

## ?? Serviços

- **backend**: Django + Gunicorn
- **frontend**: Vue.js com Vite (modo dev)
- **db**: PostgreSQL 15 com volume persistente

---

## ?? Variáveis de Ambiente (`.env.example`)

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=fazenergy
POSTGRES_USER=fazadmin
POSTGRES_PASSWORD=fazpass
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

> ?? Este setup é focado em ambiente local com Docker + WSL2. Em produção, recomenda-se separar frontend/backend e configurar nginx, CI/CD e builds otimizados.