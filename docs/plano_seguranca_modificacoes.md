# Plano de Segurança para Modificações · VetLândia

> Objetivo: blindar a evolução da plataforma (produção com dados reais) contra
> perda de dados e quebras. Pré-requisito das Regras 14 e 15 do projeto.
> Contexto: Railway + PostgreSQL. Ambientes hoje: localhost + produção. Sem backup.

## Prioridade 0 — BACKUP (antes de qualquer migration)

Hoje não há backup: uma migration ruim é irreversível na prática. Resolver primeiro.

1. **Snapshot manual agora** (independente de plano), via `pg_dump` usando a
   *connection string pública* do Postgres no Railway:
   ```bash
   pg_dump "$DATABASE_URL_PUBLICA" -Fc -f vetlandia_prod_$(date +%Y%m%d_%H%M).dump
   ```
   (Railway → serviço Postgres → Connect → "Public Network" URL.)

2. **Backups automáticos do Railway**: no serviço Postgres → aba *Backups* →
   ativar agendamento diário + tirar um backup manual imediato.

3. **Testar restauração** ao menos uma vez (em local ou staging):
   ```bash
   pg_restore --clean --no-owner -d "$DATABASE_URL_DESTINO" vetlandia_prod_*.dump
   ```
   Backup que nunca foi restaurado não é backup confiável.

4. **Backup pré-migration**: tirar um dump imediatamente antes de aplicar cada
   migration em produção (automatizável em `scripts/backup_prod.sh`).

## Prioridade 1 — Ambiente de STAGING

Sem staging, todo teste acontece em produção. Railway suporta múltiplos
*environments* por projeto.

1. Criar environment `staging` (duplica os serviços) com **Postgres próprio**.
2. Apontar o deploy da branch de trabalho para `staging`.
3. **Restaurar uma cópia dos dados de produção** no staging para testar
   migrations com dados realistas.
4. Validar cada módulo no staging antes de ir para produção.

## Prioridade 2 — Disciplina de migrations

- Toda migration com `downgrade()` funcional (reversível — Regra 14).
- Apenas **aditivo**: novas tabelas / colunas *nullable* (ou com default).
  Nunca `DROP`/`RENAME` no mesmo release.
- Testar localmente: `alembic upgrade head` → `alembic downgrade -1` → `upgrade`
  de novo, sobre uma cópia dos dados.
- **Atenção ao auto-deploy**: hoje o `startCommand` do Railway roda
  `alembic upgrade head` automaticamente a cada deploy — uma migration falha
  atinge a produção sozinha. Mitigação: validar SEMPRE no staging primeiro.

## Prioridade 3 — Fluxo de branches

- Um módulo por branch → PR → revisão → merge → deploy (Regras 3–6).
- Nunca push direto em `main` (Regras 1–2).
- (Opcional) Branch protection no GitHub exigindo PR para `main`.

## Prioridade 4 — Rede de segurança na aplicação

- Trocar o "Reprovar = DELETE" do admin por estado reversível (Módulo 9).
- (Opcional) Cron de backup lógico (Railway cron ou GitHub Action com `pg_dump`).

## Backup automático por deploy (IMPLEMENTADO na branch `seguranca/backup-pre-deploy`)

Mecanismo: antes de `alembic upgrade head`, o `startCommand` chama
`scripts/backup_before_migrate.sh`, que tira um `pg_dump` (formato custom),
grava num **Railway Volume** e mantém as **últimas 3 versões** (rotação).
É best-effort: se falhar, loga e NÃO bloqueia a subida do app; faz 1 backup por
deploy (marcado por `RAILWAY_DEPLOYMENT_ID`, não a cada restart).

### Runbook de ativação no Railway (necessário para o mecanismo funcionar)
1. **Criar o Volume**: serviço do app → *Settings → Volumes* → novo volume com
   *mount path* = `/backups`.
2. **Disponibilizar o `pg_dump` na imagem**: adicionar a variável de ambiente
   `NIXPACKS_APT_PKGS=postgresql-client` no serviço do app. (Reversível, sem
   mexer no build em código.)
   - ⚠️ O `pg_dump` precisa ser de versão **>= a major do servidor** (ex.: PG 16).
     Se o log mostrar "server version mismatch", trocar por um cliente versionado
     (`postgresql-client-16`).
3. (Opcional) Ajustar `KEEP_BACKUPS` (default 3) e `BACKUP_DIR` (default `/backups`).
4. **Merge da branch + deploy.** No primeiro deploy, conferir nos logs:
   `[backup] Backup concluído (...)`.

### Restaurar um backup
```bash
# listar dumps no volume (via shell do serviço Railway)
ls -1t /backups/vetlandia_*.dump
# restaurar para um banco destino
pg_restore --clean --no-owner -d "$DATABASE_URL_DESTINO" /backups/vetlandia_<arquivo>.dump
```

### Limitação
Protege contra erro de migration / perda de dados. **Não** protege contra perda
do projeto/conta Railway inteira (para isso, backup externo — R2/S3). Os backups
nativos diários do Postgres no painel ficam como camada complementar recomendada.

## Checklist antes de cada migration em produção
- [ ] Backup recente testado existe
- [ ] Migration validada no staging com dados realistas
- [ ] `downgrade()` testado
- [ ] Mudança é aditiva (sem drop/rename)
- [ ] Revisão da branch/PR feita
</content>
