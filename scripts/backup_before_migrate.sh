#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Backup automático do PostgreSQL ANTES de cada migration (a cada deploy).
#
# Roda no startCommand do Railway, imediatamente antes de `alembic upgrade head`,
# capturando o estado do banco PRÉ-migration. Grava o dump num diretório
# persistente (Railway Volume) e mantém apenas as últimas N versões (rotação).
#
# DESENHO DE SEGURANÇA (best-effort, NÃO derruba o app):
#   - Se algo falhar (volume ausente, pg_dump indisponível, etc.), apenas LOGA
#     e sai com 0, para nunca impedir a subida do app. O startCommand chama este
#     script com ";" justamente para que sua falha não bloqueie o deploy.
#   - Faz 1 backup por DEPLOY (não a cada reinício do container), usando o
#     RAILWAY_DEPLOYMENT_ID como marcador.
#
# Variáveis de ambiente:
#   DATABASE_URL          (obrigatória) — string de conexão do Postgres
#   BACKUP_DIR            (default /backups) — ponto de montagem do Volume
#   KEEP_BACKUPS          (default 3) — quantas versões manter
#   RAILWAY_DEPLOYMENT_ID (injetada pelo Railway) — id do deploy atual
# ──────────────────────────────────────────────────────────────────────────────

BACKUP_DIR="${BACKUP_DIR:-/backups}"
KEEP_BACKUPS="${KEEP_BACKUPS:-3}"
log() { echo "[backup] $*"; }

# 1) Pré-condições — qualquer ausência => pula (best-effort)
if [ -z "${DATABASE_URL:-}" ]; then
  log "DATABASE_URL não definida — pulando backup."
  exit 0
fi
if ! command -v pg_dump >/dev/null 2>&1; then
  log "pg_dump não encontrado na imagem — pulando backup. (Instale o cliente Postgres; ver runbook.)"
  exit 0
fi
if ! mkdir -p "$BACKUP_DIR" 2>/dev/null || [ ! -w "$BACKUP_DIR" ]; then
  log "BACKUP_DIR '$BACKUP_DIR' inexistente/sem escrita — Volume não montado? Pulando backup."
  exit 0
fi

# 2) Deduplicação por deploy — não re-dumpar a cada restart do container
DEPLOY_ID="${RAILWAY_DEPLOYMENT_ID:-manual-$(date +%Y%m%d%H%M%S)}"
MARKER="$BACKUP_DIR/.last_deploy"
if [ -f "$MARKER" ] && [ "$(cat "$MARKER" 2>/dev/null)" = "$DEPLOY_ID" ]; then
  log "Deploy $DEPLOY_ID já tem backup — pulando (provável restart do container)."
  exit 0
fi

# 3) Dump (formato custom -Fc, compactado e restaurável com pg_restore)
TS="$(date +%Y%m%d_%H%M%S)"
OUT="$BACKUP_DIR/vetlandia_${TS}_${DEPLOY_ID}.dump"
log "Iniciando pg_dump -> $OUT"
if pg_dump "$DATABASE_URL" -Fc -f "$OUT" 2>/tmp/pg_dump_err; then
  SIZE="$(du -h "$OUT" 2>/dev/null | cut -f1)"
  log "Backup concluído ($SIZE): $(basename "$OUT")"
  echo "$DEPLOY_ID" > "$MARKER"
else
  log "FALHA no pg_dump: $(cat /tmp/pg_dump_err 2>/dev/null | tail -1)"
  rm -f "$OUT" 2>/dev/null
  exit 0   # best-effort: não bloqueia o deploy
fi

# 4) Rotação — mantém apenas as últimas KEEP_BACKUPS versões
COUNT="$(ls -1t "$BACKUP_DIR"/vetlandia_*.dump 2>/dev/null | wc -l | tr -d ' ')"
if [ "$COUNT" -gt "$KEEP_BACKUPS" ]; then
  ls -1t "$BACKUP_DIR"/vetlandia_*.dump | tail -n +"$((KEEP_BACKUPS + 1))" | while read -r old; do
    log "Removendo backup antigo: $(basename "$old")"
    rm -f "$old"
  done
fi

log "Backups atuais no volume:"
ls -1t "$BACKUP_DIR"/vetlandia_*.dump 2>/dev/null | sed 's/^/[backup]   /'
exit 0
