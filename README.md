# Financeiro

Aplicativo web de finanças pessoais/familiares: planejar o orçamento anual, acompanhar o realizado, fechar meses e simular compras.

Requisitos e decisões em [docs/](docs/); fonte de verdade: `docs/App Finanças – Requisitos Funcionais.md`.

## Desenvolvimento

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Testes e lint:

```powershell
pytest
ruff check . ; ruff format .
```

## Configuração

Variáveis de ambiente (arquivo `.env` local ou painel da Vercel): `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`. Sem `DATABASE_URL` usa SQLite local. Veja `.env.example`.

## Implantação na Vercel

1. Crie um banco PostgreSQL (ex.: integração Neon no Marketplace da Vercel) e configure `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` no projeto.
2. A Vercel detecta o `manage.py`, usa `WSGI_APPLICATION` e roda `collectstatic` no build.
3. Migrations e criação de usuários rodam da sua máquina contra o banco de produção:

```powershell
vercel pull
$env:ENV_FILE = ".env.local"
python manage.py migrate
python manage.py createsuperuser
Remove-Item Env:ENV_FILE
```

Nunca versione `.env`, `.env.local` nem segredos.
