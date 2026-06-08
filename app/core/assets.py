import time

# Versão dos assets estáticos (CSS/JS) para cache-busting.
# Calculada uma vez por processo: cada deploy reinicia o processo e gera
# uma nova versão, forçando navegador e CDN (Cloudflare) a buscar o arquivo novo.
ASSET_VERSION = str(int(time.time()))
