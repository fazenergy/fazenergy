
# ⚡ FazEnergy

Sistema de gerenciamento de afiliados com Django no backend, Vue 3 + Vite no frontend e PostgreSQL como banco de dados. Containerizado com Docker para facilitar o desenvolvimento local 🚀

---

## 🧰 Tecnologias Utilizadas

- Python 3.11
- Django 5.2
- Vue 3 + Vite
- PostgreSQL 15
- Docker & Docker Compose
- CKEditor
- Axios
- Tailwind CSS (se aplicável)

---

## 🐳 Instalação com Docker

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/fazenergy.git
cd fazenergy
```

## 📁 Estrutura de Pastas
```
fazenergy/
├── backend/            # Projeto Django (apps: core, plans, finance, etc.)
│   └── manage.py
├── frontend/           # Projeto Vue + Vite
│   └── src/
├── docker-compose.yml
└── README.md
```

---

### 2. Copie os arquivos `.env`

Crie os arquivos de ambiente:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Pegue o arquivo .env com desenvolvedor e substitua.

### 3. Suba os containers

```bash
docker compose up --build
```

---


## 🗃️ Migrations

> ⚠️ Certifique-se de que a base esteja limpa antes da primeira migração.

Dentro do container backend:

```bash
docker exec -it fazenergy-backend python manage.py migrate
```

---

## 👤 Usuário Admin

Você pode criar um superusuário para acessar o painel admin, é usado para entrar na aplicação:

```bash
docker exec -it fazenergy-backend python manage.py createsuperuser
```

---

## 🔌 Acessos

| Serviço         | URL                        |
| --------------- | ---------------------------|
| Frontend (Vue)  | http://localhost:5173       |
| Backend (Django)| http://localhost:8000       |
| Admin Django    | http://localhost:8000/admin |
| PostgreSQL      | localhost:5432              |

---

## 🛡️ Segurança

- ⚠️ O CKEditor 4.x possui [vulnerabilidades conhecidas](https://ckeditor.com/ckeditor-4-support/).
- Para produção, use WSGI/ASGI (ex: Gunicorn, Uvicorn) e HTTPS com Nginx ou similar.

---

