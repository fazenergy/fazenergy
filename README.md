# README.md

# FazEnergy

Ambiente de desenvolvimento local com Docker, Django (backend), Vue.js (frontend) e PostgreSQL.

---

## Como rodar o projeto localmente

```bash
git clone <repo-url>
cd FazEnergy
cp .env.example .env
docker-compose up --build
```

- Backend Django: http://localhost:8000
- Frontend Vue.js: http://localhost:5173

### Após subir os containers:

```bash
# Acessar o container do backend
docker exec -it fazenergy-backend bash

# Rodar migrações do Django
python manage.py migrate

# Criar um superusuário
python manage.py createsuperuser

# (Opcional) Coletar arquivos estáticos
python manage.py collectstatic
```

---

## Estrutura do Projeto

```
FazEnergy/
├── backend/             # Django Backend
│   └── Dockerfile
├── frontend/            # Vue Frontend
│   └── Dockerfile
├── docker-compose.yml   # Orquestra todos os serviços
├── .env                 # Variáveis de ambiente
└── .env.example         # Modelo de variáveis
```

---

## Comandos úteis

```bash
# Acessar container do backend
docker exec -it fazenergy-backend bash

# Rodar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### Teste rápido – Integração REVO (contractor)

```bash
curl --location 'http://127.0.0.1:8000/api/contractor/revo/simulation/' \
  --header 'Content-Type: application/json' \
  --data-raw '{
  "contractor_id": 1,
  "zip_code": "38400668",
  "property_type": "Casa",
  "owner": "Próprio",
  "energy_provider_id": 8,
  "consumer_unit": "B200000",
  "consumer_group": "A4",
  "fiscal_number": "01539603610",
  "seller_email": "raphael@fazendadosol.com.br",
  "monthly_consumption": {"january":500,"february":480,"march":510,"april":490,"may":530,"june":540,"july":560,"august":550,"september":500,"october":510,"november":495,"december":525},
  "lead_actors": [{
    "actor": "contractor",
    "name": "Nome do cliente",
    "cellphone": "11999998888",
    "email": "cliente@exemplo.com",
    "cpf": "01539603610",
    "zip_code": "38400668",
    "address": "Rua/Avenida",
    "number": "100",
    "neighborhood": "Bairro",
    "city": "Uberlândia",
    "st": "MG"
  }]}'
```

Resposta esperada (resumo):

```json
{
  "revo": { /* ecoa a resposta da REVO */ },
  "proposal_id": 2,
  "result_id": 1,
  "proposal": { /* dados persistidos em ContractorProposal */ },
  "result": { /* dados persistidos em ContractorProposalResult */ }
}
```

---

## Serviços

- backend: Django
- frontend: Vue.js com Vite (modo dev)
- db: PostgreSQL 15 com volume persistente

---

## Variáveis de Ambiente (.env.example)

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

> Este setup é focado em ambiente local com Docker + WSL2. Em produção, recomenda-se separar frontend/backend e configurar nginx, CI/CD e builds otimizados.