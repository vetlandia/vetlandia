# Setup Local - VetLândia

## Problema Atual: Python 3.14

**Status:** Sistema com Python 3.14, mas Pydantic/PyO3 ainda não suportam (max 3.13).

**Soluções:**

### Opção 1: Instalar Python 3.12 (Recomendado)

```bash
# Homebrew
brew install python@3.12

# Criar venv com Python 3.12
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Opção 2: Usar pyenv

```bash
# Instalar pyenv
brew install pyenv

# Instalar Python 3.12
pyenv install 3.12.7
pyenv local 3.12.7

# Criar venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Opção 3: Forward Compatibility (Temporário - não recomendado produção)

```bash
# Força build com Python 3.14
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt
```

---

## Setup Completo (após Python 3.12 instalado)

```bash
# 1. Clonar repo
git clone https://github.com/vetlandia/vetlandia.git
cd vetlandia

# 2. Criar ambiente virtual
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env

# Editar .env:
# - DATABASE_URL (PostgreSQL local ou Railway)
# - SECRET_KEY (gerar nova: python -c "import secrets; print(secrets.token_urlsafe(32))")

# 5. Setup banco de dados local (opcional)
brew install postgresql@16
brew services start postgresql@16

# Criar database
createdb vetlandia_dev

# 6. Rodar migrations
alembic upgrade head

# 7. Iniciar servidor
uvicorn app.main:app --reload

# Abrir: http://localhost:8000
```

---

## Comandos Úteis

```bash
# Criar nova migration
alembic revision --autogenerate -m "description"

# Aplicar migrations
alembic upgrade head

# Reverter migration
alembic downgrade -1

# Ver migrations
alembic history

# Formatar código
ruff format app/

# Lint
ruff check app/

# Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Variáveis de Ambiente

```bash
# .env
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@localhost:5432/vetlandia_dev
SECRET_KEY=seu-secret-key-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=VetLândia
APP_VERSION=1.0.0
```

---

## Próximos Passos

Após setup local funcionando:

1. Continuar task #5: criar primeira migration
2. Implementar schemas Pydantic
3. Implementar services básicos
4. Criar templates + CSS
5. Deploy Railway

---

**Bloqueio atual:** Aguardando Python 3.12 para prosseguir com instalação de dependências.
