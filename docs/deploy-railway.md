# Deploy VetLândia no Railway

## Pré-requisitos

✅ Conta Railway criada  
✅ Conta GitHub conectada ao Railway  
✅ Repositório GitHub do projeto  
✅ Domínio vetlandia.com.br configurado no Cloudflare

---

## Passo 1: Preparar Repositório GitHub

```bash
# Commit todas as alterações
git add .
git commit -m "feat: Design premium mobile-first implementado"

# Push para GitHub
git push origin main
```

---

## Passo 2: Criar Projeto no Railway

1. Acesse https://railway.app/
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório `vetlandia/vetlandia`
5. Railway detecta Python automaticamente

---

## Passo 3: Adicionar PostgreSQL

1. No projeto Railway, clique em "+ New"
2. Selecione "Database" → "PostgreSQL"
3. Railway provisiona automaticamente
4. A variável `DATABASE_URL` é injetada automaticamente

---

## Passo 4: Configurar Variáveis de Ambiente

No Railway, vá em "Variables" e adicione:

```bash
ENVIRONMENT=production

SECRET_KEY=<GERAR_NOVO>
# Gerar com: python -c "import secrets; print(secrets.token_urlsafe(32))"

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=VetLândia
APP_VERSION=1.0.0
```

**IMPORTANTE:** O `DATABASE_URL` já é fornecido automaticamente pelo PostgreSQL do Railway.

---

## Passo 5: Verificar Build

Railway usa o `railway.json` para configurar build:

```json
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

O build:
1. Instala Python 3.12
2. Instala dependências do `requirements.txt`
3. Roda migrations (`alembic upgrade head`)
4. Inicia servidor FastAPI

---

## Passo 6: Conectar Domínio Custom

### No Railway:

1. Vá em "Settings" → "Domains"
2. Clique em "Custom Domain"
3. Digite: `vetlandia.com.br`
4. Railway mostra o CNAME target (ex: `xyz.up.railway.app`)

### No Cloudflare:

1. Acesse Cloudflare DNS para `vetlandia.com.br`
2. Adicione registro CNAME:
   ```
   Type: CNAME
   Name: @
   Target: <railway-url>.up.railway.app
   Proxy status: Proxied (laranja)
   TTL: Auto
   ```

3. Adicione também para www:
   ```
   Type: CNAME
   Name: www
   Target: <railway-url>.up.railway.app
   Proxy status: Proxied
   TTL: Auto
   ```

4. Em SSL/TLS Settings:
   - SSL Mode: Full (strict)
   - Edge Certificates: ON
   - Always Use HTTPS: ON

---

## Passo 7: Verificar Deploy

1. Railway faz deploy automático
2. Aguarde build completar (2-3 minutos)
3. Acesse https://vetlandia.com.br
4. Verifique:
   - ✅ HTTPS funcionando
   - ✅ Home page carrega
   - ✅ Sem erros 500
   - ✅ Database conectado

---

## Comandos Úteis

### Ver logs em tempo real:
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link ao projeto
railway link

# Ver logs
railway logs
```

### Rodar migration manual:
```bash
railway run alembic upgrade head
```

### Acessar database:
```bash
railway connect PostgreSQL
```

---

## Troubleshooting

### Erro: "Module not found"
- Verificar `requirements.txt` tem todas dependências
- Railway buildou com Python correto? (ver logs)

### Erro: "Database connection failed"
- Variável `DATABASE_URL` configurada?
- PostgreSQL está running?
- Formato correto: `postgresql+psycopg://...`

### Erro 500 na home:
- Ver logs: `railway logs`
- Verificar migrations rodaram: `alembic current`

### Domínio não resolve:
- DNS propagou? (pode levar até 48h)
- CNAME configurado corretamente?
- Cloudflare proxy ativo (laranja)?

---

## Monitoramento

### Métricas Railway:
- CPU/Memory usage
- Request count
- Error rate
- Deploy history

### Cloudflare Analytics:
- Visitors
- Bandwidth
- Threats blocked
- Cache hit rate

---

## Backups

Railway faz backup automático do PostgreSQL.

Para backup manual:
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

---

## Custos Estimados

**Railway:**
- Hobby Plan: $5/mês
- PostgreSQL: incluído

**Cloudflare:**
- DNS + SSL: Grátis

**Total:** ~$5/mês

---

## Próximos Passos Pós-Deploy

1. ✅ Criar primeiro usuário veterinário
2. ✅ Criar primeira clínica
3. ✅ Publicar primeiro caso clínico
4. ✅ Testar fluxo completo
5. ✅ Configurar Google Analytics (futuro)
6. ✅ Configurar Sentry (error tracking - futuro)

---

## Comandos Deploy Rápido

```bash
# 1. Commit + Push
git add . && git commit -m "update" && git push

# 2. Railway faz deploy automático!
# 3. Acesse vetlandia.com.br em ~2min
```

---

**Status:** Deploy configurado e pronto! 🚀
