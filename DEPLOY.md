# Deploy VetLândia - Railway + vetlandia.com.br

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Conta no [GitHub](https://github.com)
3. Domínio vetlandia.com.br configurado (Registro.br ou provedor DNS)
4. CLI do Railway instalado (opcional): `npm i -g @railway/cli`

## 🚀 Passo a Passo - Deploy no Railway

### 1. Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha o repositório `vetlandia/vetlandia`
6. Railway detectará automaticamente que é Python/FastAPI

### 2. Adicionar PostgreSQL

1. No projeto Railway, clique em "+ New"
2. Selecione "Database" → "Add PostgreSQL"
3. Railway criará automaticamente o banco e definirá `DATABASE_URL`

### 3. Configurar Variáveis de Ambiente

No painel Railway, vá em "Variables" e adicione:

```bash
ENVIRONMENT=production

# DATABASE_URL é gerado automaticamente pelo Railway PostgreSQL
# Não precisa adicionar manualmente

# Gerar SECRET_KEY seguro:
# Execute localmente: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<cole-aqui-o-secret-key-gerado>

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=VetLândia
APP_VERSION=1.0.0
```

**⚠️ IMPORTANTE:** Nunca use `dev-secret-key-change-in-production` em produção!

### 4. Deploy Automático

Railway fará deploy automaticamente após configurar as variáveis:

1. Instala dependências do `requirements.txt`
2. Executa migrations: `alembic upgrade head`
3. Inicia servidor: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Aguarde alguns minutos. Railway fornecerá uma URL temporária (ex: `vetlandia-production.up.railway.app`)

### 5. Testar Deploy

Acesse a URL fornecida pelo Railway e teste:

- ✅ Homepage carrega
- ✅ `/health` retorna `{"status": "ok"}`
- ✅ Cadastro de tutor funciona
- ✅ Login funciona
- ✅ Busca de veterinários funciona

## 🌐 Configurar Domínio vetlandia.com.br

### Opção A: DNS direto no Railway (Recomendado)

1. No Railway, vá em "Settings" → "Domains"
2. Clique em "Custom Domain"
3. Digite: `vetlandia.com.br`
4. Railway mostrará os registros DNS necessários

5. No painel do Registro.br (ou seu provedor DNS):
   - Adicione registro `A` apontando para o IP fornecido
   - Ou `CNAME` para o domínio Railway (se permitido)

6. Configure também `www.vetlandia.com.br`:
   - Adicione `CNAME www` → `vetlandia.com.br`

7. Aguarde propagação DNS (até 48h, geralmente minutos)

### Opção B: Cloudflare + Railway

1. Adicione domínio no Cloudflare
2. Mude nameservers no Registro.br para Cloudflare
3. No Cloudflare, adicione registro:
   ```
   Type: CNAME
   Name: @
   Target: <seu-projeto>.up.railway.app
   Proxy status: Proxied (laranja)
   ```

4. Adicione também para www:
   ```
   Type: CNAME
   Name: www
   Target: vetlandia.com.br
   Proxy status: Proxied
   ```

5. No Railway, adicione domínio customizado: `vetlandia.com.br`

**Benefícios Cloudflare:**
- ✅ SSL automático
- ✅ CDN global
- ✅ Proteção DDoS
- ✅ Cache de assets estáticos
- ✅ Analytics

## 📊 Monitoramento

### Logs do Railway

```bash
# Via CLI
railway logs

# Ou via Dashboard
Projeto → Deployments → View Logs
```

### Health Check

Configure em **Settings → Health Check**:
- Path: `/health`
- Interval: 60 segundos

### Métricas

Railway mostra automaticamente:
- CPU usage
- Memory usage
- Request count
- Response time

## 🔄 Updates e CI/CD

Railway está conectado ao GitHub. Para atualizar:

```bash
# 1. Fazer alterações localmente
git add .
git commit -m "Descrição das mudanças"

# 2. Push para GitHub
git push origin main

# 3. Railway detecta e faz deploy automático
```

Rollback (se necessário):
- Dashboard Railway → Deployments → Selecione deploy anterior → "Redeploy"

## 🗄️ Backup do Banco

### Manual via Railway CLI

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Link ao projeto
railway link

# Dump do banco
railway run pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

### Automático (recomendado)

1. Railway Pro tem backups automáticos
2. Ou configure serviço externo (ex: [PGBackups](https://pgbackups.com))

## 📈 Scaling

Railway escala automaticamente, mas você pode configurar:

- **Settings → Resources**
  - Memory: 512MB - 8GB
  - CPU: 1-8 vCPUs
  - Replicas: 1-10 (Pro plan)

## 🔐 Segurança

✅ **Checklist Pré-Deploy:**

- [ ] `SECRET_KEY` gerado com `secrets.token_urlsafe(32)`
- [ ] `ENVIRONMENT=production`
- [ ] `.env` está no `.gitignore`
- [ ] Domínio com HTTPS (Railway ou Cloudflare)
- [ ] DATABASE_URL usa `postgresql+psycopg://` (não `psycopg2`)
- [ ] CORS configurado corretamente (se necessário)
- [ ] Migrations testadas localmente

## 📞 Suporte

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Logs de erro:** `railway logs --tail`

## 💰 Custos Estimados

**Railway Hobby Plan (Grátis):**
- $5 crédito/mês
- ~500h de uptime
- PostgreSQL incluído
- Suficiente para testes/MVP

**Railway Pro Plan ($20/mês):**
- $20 créditos incluídos
- Uptime 100%
- Backups automáticos
- Custom domains ilimitados
- Métricas avançadas

**Estimativa VetLândia (médio tráfego):**
- App: ~$5-10/mês
- PostgreSQL: ~$3-5/mês
- **Total: ~$8-15/mês**
