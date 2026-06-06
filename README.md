# VetLândia

**Confiança para quem cuida. Conhecimento para quem trata.**

Ecossistema digital para o mercado veterinário brasileiro.

## Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** Jinja2 Templates + CSS + JavaScript
- **Deploy:** Railway
- **DNS/SSL:** Cloudflare

## Setup Local

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# Rodar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## Documentação

- [Identidade Visual](docs/identidade-visual.md)
- [Arquitetura](docs/arquitetura.md)

## Status

MVP em desenvolvimento.
