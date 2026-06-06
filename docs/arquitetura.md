# Arquitetura VetLândia

**Versão:** 1.0  
**Data:** 2026-06-06  
**Status:** Aprovada

---

## Stack Técnica

### Backend
- **Framework:** FastAPI 0.110+
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic
- **Validação:** Pydantic v2
- **Auth:** JWT (python-jose)
- **Password:** bcrypt
- **Database:** PostgreSQL 15+

### Frontend
- **Templates:** Jinja2
- **Styling:** CSS puro (sem framework)
- **JavaScript:** Vanilla JS (progressivo)
- **Icons:** Heroicons (CDN)

### Infraestrutura
- **Hosting:** Railway
- **Database:** Railway PostgreSQL
- **DNS/SSL:** Cloudflare
- **Static Files:** Servidos pelo FastAPI (MVP)

### Dev Tools
- **Python:** 3.11+
- **Package Manager:** pip + venv
- **Code Quality:** ruff (linter + formatter)
- **Env Management:** python-dotenv

---

## Arquitetura Backend

### Camadas

```
vetlandia/
├── app/
│   ├── models/          # SQLAlchemy models (DB schema)
│   ├── schemas/         # Pydantic schemas (validação I/O)
│   ├── services/        # Lógica de negócio
│   ├── routers/         # FastAPI routers (endpoints)
│   ├── templates/       # Jinja2 templates
│   ├── static/          # CSS, JS, imagens
│   ├── core/            # Config, segurança, dependencies
│   └── utils/           # Helpers reutilizáveis
```

### Responsabilidades

**Models** (`app/models/`)
- Definição de tabelas (SQLAlchemy)
- Relacionamentos
- Constraints
- Apenas estrutura, sem lógica

**Schemas** (`app/schemas/`)
- Validação de input (requests)
- Serialização de output (responses)
- Pydantic models
- Conversão de tipos

**Services** (`app/services/`)
- Lógica de negócio
- Orquestração de operações
- Transações complexas
- Regras de validação de negócio

**Routers** (`app/routers/`)
- Definição de endpoints HTTP
- Validação via schemas
- Delegação para services
- Tratamento de erros HTTP

**Core** (`app/core/`)
- Configuração (settings)
- Segurança (auth, passwords)
- Database session
- Dependencies injetáveis

**Utils** (`app/utils/`)
- Funções auxiliares
- Helpers reutilizáveis
- Formatação, slugify, etc

---

## Princípios Arquiteturais

### 1. Separation of Concerns
- Routers não têm lógica de negócio
- Services não conhecem HTTP
- Models não têm validação de input

### 2. Dependency Injection
```python
# Exemplo
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/veterinarios")
def list_vets(db: Session = Depends(get_db)):
    # db injetado automaticamente
```

### 3. Schema-Driven Development
- Input sempre validado por Pydantic
- Output sempre serializado por Pydantic
- Nunca retornar models direto

### 4. Fail Fast
- Validação no ponto de entrada
- Erros explícitos e informativos
- HTTP status codes corretos

---

## Estrutura de Arquivos

```
vetlandia/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + routers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings (BaseSettings)
│   │   ├── database.py         # SQLAlchemy engine + session
│   │   ├── security.py         # Password hash, JWT
│   │   └── dependencies.py     # Injetáveis (get_db, get_current_user)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User, Tutor
│   │   ├── veterinarian.py     # Veterinarian
│   │   ├── clinic.py           # Clinic
│   │   ├── review.py           # Review
│   │   └── case.py             # ClinicalCase, CaseComment
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # UserCreate, UserResponse, Login
│   │   ├── veterinarian.py     # VetCreate, VetUpdate, VetResponse
│   │   ├── clinic.py           # ClinicCreate, ClinicResponse
│   │   ├── review.py           # ReviewCreate, ReviewResponse
│   │   └── case.py             # CaseCreate, CaseResponse, CommentCreate
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, registro, JWT
│   │   ├── veterinarian.py     # CRUD veterinários + busca
│   │   ├── clinic.py           # CRUD clínicas + busca
│   │   ├── review.py           # Criar/listar avaliações
│   │   └── case.py             # CRUD casos clínicos + comentários
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pages.py            # Rotas HTML (home, busca, perfis)
│   │   ├── auth.py             # /login, /cadastro (POST)
│   │   ├── veterinarians.py    # API veterinários
│   │   ├── clinics.py          # API clínicas
│   │   ├── reviews.py          # API avaliações
│   │   └── cases.py            # API casos clínicos
│   │
│   ├── templates/
│   │   ├── base.html           # Template base
│   │   ├── home.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── veterinarian/
│   │   │   ├── profile.html
│   │   │   └── search.html
│   │   ├── clinic/
│   │   │   ├── profile.html
│   │   │   └── search.html
│   │   └── case/
│   │       ├── feed.html
│   │       ├── detail.html
│   │       └── create.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css        # Reset + variáveis CSS
│   │   │   ├── components.css  # Botões, cards, badges
│   │   │   └── pages.css       # Estilos específicos páginas
│   │   ├── js/
│   │   │   └── main.js         # JS global (se necessário)
│   │   └── images/
│   │       └── logo.svg        # (futuro)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── slugify.py          # Geração de slugs
│       └── validators.py       # Validadores customizados (CRMV)
│
├── alembic/
│   ├── versions/               # Migrations
│   └── env.py
│
├── tests/                      # (futuro - opcional MVP)
│
├── .env.example
├── .env                        # Gitignored
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── docs/                       # Já existente
    ├── arquitetura.md
    └── identidade-visual.md
```

---

## Database Schema

### Users (base para todos usuários)

```python
users
├── id: UUID (PK)
├── email: String(255) UNIQUE NOT NULL
├── password_hash: String(255) NOT NULL
├── user_type: Enum('tutor', 'veterinarian', 'clinic') NOT NULL
├── is_active: Boolean DEFAULT True
├── created_at: DateTime
└── updated_at: DateTime
```

### Tutors

```python
tutors
├── id: UUID (PK)
├── user_id: UUID (FK users.id) UNIQUE NOT NULL
├── full_name: String(255) NOT NULL
├── phone: String(20)
└── created_at: DateTime
```

### Veterinarians

```python
veterinarians
├── id: UUID (PK)
├── user_id: UUID (FK users.id) UNIQUE NOT NULL
├── full_name: String(255) NOT NULL
├── crmv: String(20) UNIQUE NOT NULL
├── specialty: String(100)
├── bio: Text
├── phone: String(20)
├── photo_url: String(500)
├── slug: String(255) UNIQUE NOT NULL
├── clinic_id: UUID (FK clinics.id) NULL
├── city: String(100)
├── state: String(2)
├── created_at: DateTime
└── updated_at: DateTime

Indexes:
- crmv (unique)
- slug (unique)
- city, state (busca)
- clinic_id (FK)
```

### Clinics

```python
clinics
├── id: UUID (PK)
├── user_id: UUID (FK users.id) UNIQUE NOT NULL
├── name: String(255) NOT NULL
├── description: Text
├── address: String(500)
├── city: String(100) NOT NULL
├── state: String(2) NOT NULL
├── zip_code: String(10)
├── phone: String(20)
├── email: String(255)
├── website: String(500)
├── logo_url: String(500)
├── slug: String(255) UNIQUE NOT NULL
├── created_at: DateTime
└── updated_at: DateTime

Indexes:
- slug (unique)
- city, state (busca)
```

### Reviews

```python
reviews
├── id: UUID (PK)
├── author_id: UUID (FK users.id) NOT NULL
├── reviewee_type: Enum('veterinarian', 'clinic') NOT NULL
├── reviewee_id: UUID NOT NULL  # ID do vet ou clínica
├── rating: Integer (1-5) NOT NULL
├── comment: Text NOT NULL
├── created_at: DateTime
└── updated_at: DateTime

Indexes:
- author_id
- reviewee_type, reviewee_id (composite)
- created_at (ordenação)

Constraints:
- UNIQUE (author_id, reviewee_type, reviewee_id)
  # Usuário avalia mesma entidade 1x
- CHECK (rating >= 1 AND rating <= 5)
- CHECK (length(comment) >= 50)
```

### Clinical Cases

```python
clinical_cases
├── id: UUID (PK)
├── author_id: UUID (FK veterinarians.id) NOT NULL
├── title: String(255) NOT NULL
├── species: String(50)
├── breed: String(100)
├── specialty: String(100)
├── content: Text NOT NULL
├── created_at: DateTime
└── updated_at: DateTime

Indexes:
- author_id
- specialty (filtro)
- created_at (ordenação)
```

### Case Comments

```python
case_comments
├── id: UUID (PK)
├── case_id: UUID (FK clinical_cases.id) NOT NULL
├── author_id: UUID (FK veterinarians.id) NOT NULL
├── content: Text NOT NULL
├── created_at: DateTime
└── updated_at: DateTime

Indexes:
- case_id (listagem)
- created_at (ordenação)
```

---

## Relacionamentos

```
User 1:1 Tutor/Veterinarian/Clinic (user_type define)

Veterinarian N:1 Clinic (veterinário vinculado a 1 clínica)

Review N:1 User (author)
Review N:1 Veterinarian/Clinic (reviewee - polimórfico)

ClinicalCase N:1 Veterinarian (author)
CaseComment N:1 ClinicalCase
CaseComment N:1 Veterinarian (author)
```

---

## Autenticação

### Fluxo

1. **Registro:**
   - POST `/auth/register` com `{email, password, user_type, ...}`
   - Cria `User` + entidade específica (Tutor/Vet/Clinic)
   - Retorna JWT

2. **Login:**
   - POST `/auth/login` com `{email, password}`
   - Valida credenciais
   - Retorna JWT

3. **Acesso protegido:**
   - Header: `Authorization: Bearer <token>`
   - Dependency `get_current_user` valida JWT
   - Injeta `User` na rota

### JWT Payload

```json
{
  "sub": "user_id",
  "user_type": "veterinarian",
  "exp": 1234567890
}
```

### Permissões MVP

- **Tutores:** avaliar, visualizar perfis
- **Veterinários:** tudo de tutores + criar casos, comentar casos
- **Clínicas:** visualizar, editar próprio perfil

---

## Validações de Negócio

### CRMV

Formato: `CRMV-UF XXXXX`

Exemplo: `CRMV-SP 12345`

```python
# Regex
r'^CRMV-[A-Z]{2}\s\d{4,6}$'
```

### Avaliações

- Mínimo 50 caracteres no comentário
- Rating 1-5
- 1 avaliação por usuário por entidade
- Tutor pode avaliar vet/clínica
- Veterinário pode avaliar clínica (futuro)

### Casos Clínicos

- Apenas veterinários podem publicar
- Título obrigatório (max 255 chars)
- Conteúdo obrigatório (min 100 chars)
- Comentários apenas veterinários

---

## Slugs

Geração automática para URLs semânticas:

**Veterinários:**
```
dra-maria-silva-sao-paulo
dr-joao-santos-rio-janeiro
```

Pattern: `{nome}-{cidade}`

**Clínicas:**
```
clinica-vet-centro-belo-horizonte
hospital-veterinario-campo-grande
```

Pattern: `{nome-clinica}-{cidade}`

**Geração:**
- Remover acentos
- Lowercase
- Substituir espaços por `-`
- Remover caracteres especiais
- Garantir unicidade (append `-2` se duplicado)

---

## Endpoints MVP

### Páginas HTML (SSR)

```
GET  /                          # Home
GET  /login                     # Login form
GET  /cadastro                  # Registro form
GET  /veterinario/{slug}        # Perfil veterinário
GET  /clinica/{slug}            # Perfil clínica
GET  /buscar/veterinarios       # Busca vets
GET  /buscar/clinicas           # Busca clínicas
GET  /casos-clinicos            # Feed casos
GET  /casos-clinicos/{id}       # Detalhe caso
GET  /casos-clinicos/criar      # Form criar caso (auth)
GET  /meu-perfil                # Perfil usuário logado (auth)
```

### API Endpoints

```
POST /api/auth/register         # Criar conta
POST /api/auth/login            # Login (retorna JWT)

GET  /api/veterinarians         # Listar/buscar vets
GET  /api/veterinarians/{id}    # Detalhe vet
POST /api/veterinarians         # Criar perfil (auth)
PUT  /api/veterinarians/{id}    # Atualizar perfil (auth)

GET  /api/clinics               # Listar/buscar clínicas
GET  /api/clinics/{id}          # Detalhe clínica
POST /api/clinics               # Criar perfil (auth)
PUT  /api/clinics/{id}          # Atualizar perfil (auth)

POST /api/reviews               # Criar avaliação (auth)
GET  /api/reviews?reviewee_type=vet&reviewee_id={id}  # Listar avaliações

GET  /api/cases                 # Listar casos
GET  /api/cases/{id}            # Detalhe caso
POST /api/cases                 # Criar caso (auth vet)
POST /api/cases/{id}/comments   # Comentar (auth vet)
```

---

## Error Handling

### HTTP Status Codes

```
200 OK                  # Sucesso
201 Created             # Recurso criado
400 Bad Request         # Validação falhou
401 Unauthorized        # Não autenticado
403 Forbidden           # Não autorizado
404 Not Found           # Recurso não existe
409 Conflict            # Duplicação (email, CRMV)
422 Unprocessable       # Validação Pydantic
500 Internal Error      # Erro servidor
```

### Response Format

```json
// Sucesso
{
  "data": {...}
}

// Erro
{
  "detail": "Mensagem de erro clara"
}

// Validação Pydantic
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Performance (MVP)

### Otimizações Triviais

```python
# N+1 queries - EVITAR
vets = db.query(Veterinarian).all()
for vet in vets:
    clinic = vet.clinic  # Query por vet!

# Correto - eager loading
vets = db.query(Veterinarian)\
    .options(joinedload(Veterinarian.clinic))\
    .all()
```

### Paginação

```python
# Query params
?page=1&per_page=20

# Default: 20 por página
# Max: 100 por página
```

### Índices

- FK sempre indexadas
- Campos de busca (city, state, specialty)
- Campos de ordenação (created_at, rating)

---

## Observabilidade MVP

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Estrutura
logger.error(
    "Failed to create review",
    extra={
        "user_id": user.id,
        "reviewee_type": review.reviewee_type,
        "error": str(e)
    }
)
```

### Logs Obrigatórios

- Erros (sempre)
- Criação de conta
- Login (sucesso/falha)
- Criação de avaliação
- Criação de caso clínico

### Formato

JSON estruturado para parsing futuro.

---

## Segurança

### Checklist MVP

- [ ] Passwords com bcrypt (rounds >= 12)
- [ ] JWT com expiração (24h)
- [ ] HTTPS obrigatório (Cloudflare)
- [ ] CORS configurado
- [ ] SQL Injection protegido (ORM)
- [ ] XSS protegido (Jinja2 auto-escape)
- [ ] CSRF tokens (forms)
- [ ] Rate limiting (futuro - Railway permite?)
- [ ] Input validation (Pydantic)
- [ ] Secrets em .env (nunca commit)

### Variáveis de Ambiente

```
DATABASE_URL=postgresql://...
SECRET_KEY=...  # JWT signing
ENVIRONMENT=development|production
```

---

## Deploy (Railway)

### Setup

1. Conectar repo GitHub
2. Detecta Python automaticamente
3. Provisiona PostgreSQL
4. Injeta `DATABASE_URL`

### Configuração

```
# Procfile (se necessário)
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Migrations

```bash
# Rodar antes do deploy
alembic upgrade head
```

---

## Testes (Opcional MVP)

Se implementar:

```python
tests/
├── test_auth.py         # Login, registro
├── test_veterinarians.py # CRUD vets
└── test_reviews.py      # Sistema avaliações

# Usar pytest + httpx
# Focus: fluxos críticos apenas
```

---

## Próximos Passos

1. ✅ Arquitetura definida
2. Criar estrutura de pastas
3. Setup inicial (requirements.txt, .env, config)
4. Models + migrations
5. Schemas
6. Services básicos
7. Routers + templates

---

**Aprovado em:** 2026-06-06  
**Próxima revisão:** Após implementação core
