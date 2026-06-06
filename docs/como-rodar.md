# Como Rodar o VetLândia Localmente

## Pré-requisitos

✅ Python 3.12 instalado  
✅ Dependências instaladas (`pip install -r requirements.txt`)  
✅ Banco de dados configurado (SQLite já criado)

## Iniciar Servidor

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload

# Ou especificar host/porta
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Acessar Aplicação

- **Home:** http://localhost:8000
- **Docs API:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Estrutura Atual

✓ Home page funcional  
✓ Sistema de design implementado (CSS)  
✓ API de autenticação (`/api/auth/login`, `/api/auth/register/*`)  
✓ Banco de dados SQLite (`vetlandia.db`)  

## Próximos Passos

Implementar:
- [ ] Páginas de login/cadastro (HTML forms)
- [ ] Perfis de veterinários e clínicas
- [ ] Sistema de busca
- [ ] Casos clínicos
- [ ] Sistema de avaliações

## Deploy (Railway)

Ver task #10 para instruções de deploy.

## Troubleshooting

**Porta 8000 ocupada:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Erro de import:**
```bash
# Verificar se está no venv
which python
# Deve mostrar: /Users/.../vetlandia/venv/bin/python
```

**Erro de database:**
```bash
# Recriar banco
rm vetlandia.db
alembic upgrade head
```
