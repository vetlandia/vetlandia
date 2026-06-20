"""Serviço de e-mail via Resend (HTTP API).

Uso:
    from app.services.email import send_email, tpl_*
    send_email(to="user@example.com", subject="Assunto", html=tpl_aprovacao(...))

Envio assíncrono em thread daemon — falhas são logadas, nunca propagadas.
Se RESEND_API_KEY não estiver configurado, os envios são ignorados silenciosamente.
"""
import logging
import threading

from app.core.config import settings

logger = logging.getLogger(__name__)

_BRAND_COLOR = "#0d9488"
_SITE_URL = "https://vetlandia.com.br"


# ── Core ─────────────────────────────────────────────────────────────────────

def send_email_sync(to: str, subject: str, html: str) -> None:
    """Envio síncrono via Resend — levanta exceção em caso de falha."""
    import resend
    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [to],
        "subject": subject,
        "html": html,
    })


def send_email(to: str, subject: str, html: str) -> None:
    """Fire-and-forget: envia em thread daemon. Nunca levanta exceção."""
    if not settings.RESEND_API_KEY:
        logger.info("RESEND_API_KEY não configurado — e-mail ignorado: %s → %s", to, subject)
        return
    if not to or "@" not in to:
        logger.warning("E-mail inválido ignorado: %r", to)
        return

    def _worker() -> None:
        try:
            send_email_sync(to, subject, html)
            logger.info("E-mail enviado → %s | %s", to, subject)
        except Exception as exc:
            logger.error("Falha ao enviar e-mail → %s | %s | %s", to, subject, exc)

    threading.Thread(target=_worker, daemon=True).start()


# ── Layout compartilhado ──────────────────────────────────────────────────────

def _wrap(body: str, preview: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>VetLândia</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
{'<div style="display:none;max-height:0;overflow:hidden;">' + preview + '</div>' if preview else ''}
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 16px;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
      <!-- Header -->
      <tr>
        <td style="background:{_BRAND_COLOR};padding:24px 32px;text-align:center;">
          <span style="font-size:1.5rem;font-weight:800;color:#fff;letter-spacing:-.5px;">🐾 VetLândia</span>
        </td>
      </tr>
      <!-- Body -->
      <tr>
        <td style="padding:32px 36px 24px;">
          {body}
        </td>
      </tr>
      <!-- Footer -->
      <tr>
        <td style="background:#f9fafb;padding:18px 36px;border-top:1px solid #e5e7eb;text-align:center;">
          <p style="margin:0;font-size:0.78rem;color:#9ca3af;">
            Você está recebendo este e-mail porque possui uma conta no
            <a href="{_SITE_URL}" style="color:{_BRAND_COLOR};text-decoration:none;">VetLândia</a>.
          </p>
        </td>
      </tr>
    </table>
  </td></tr>
</table>
</body>
</html>"""


def _btn(label: str, url: str) -> str:
    return (
        f'<p style="text-align:center;margin:24px 0 0;">'
        f'<a href="{url}" style="display:inline-block;background:{_BRAND_COLOR};color:#fff;'
        f'font-weight:700;font-size:0.95rem;padding:12px 28px;border-radius:8px;'
        f'text-decoration:none;">{label}</a></p>'
    )


def _h1(text: str) -> str:
    return f'<h1 style="margin:0 0 16px;font-size:1.3rem;font-weight:700;color:#111827;">{text}</h1>'


def _p(text: str) -> str:
    return f'<p style="margin:0 0 12px;font-size:0.95rem;color:#374151;line-height:1.6;">{text}</p>'


def _quote(text: str) -> str:
    return (
        f'<blockquote style="margin:16px 0;padding:12px 16px;background:#f0fdfa;'
        f'border-left:4px solid {_BRAND_COLOR};border-radius:0 6px 6px 0;'
        f'font-size:0.9rem;color:#374151;line-height:1.6;">{text}</blockquote>'
    )


# ── Templates ─────────────────────────────────────────────────────────────────

def tpl_boas_vindas_tutor(name: str) -> str:
    body = (
        _h1(f"Bem-vindo(a) ao VetLândia, {name.split()[0]}!")
        + _p("Sua conta foi criada com sucesso. Agora você pode encontrar os melhores veterinários e clínicas para cuidar dos seus pets.")
        + _p("Explore perfis verificados, leia avaliações de outros tutores e agende consultas com facilidade.")
        + _btn("Acessar VetLândia", _SITE_URL)
    )
    return _wrap(body, preview=f"Bem-vindo(a), {name.split()[0]}! Sua conta está pronta.")


def tpl_cadastro_recebido(name: str, tipo: str) -> str:
    tipo_label = "veterinário(a)" if tipo == "veterinarian" else "clínica"
    body = (
        _h1(f"Cadastro recebido, {name.split()[0]}!")
        + _p(f"Obrigado por se cadastrar como <strong>{tipo_label}</strong> no VetLândia.")
        + _p("Nossa equipe irá analisar seu perfil em breve. Assim que aprovado, você receberá outro e-mail e seu perfil ficará visível para todos os tutores.")
        + _p("Enquanto isso, você pode completar as informações do seu perfil acessando sua conta.")
        + _btn("Acessar minha conta", f"{_SITE_URL}/minha-conta")
    )
    return _wrap(body, preview="Recebemos seu cadastro! Em breve nossa equipe irá analisá-lo.")


def tpl_aprovacao(name: str, tipo: str, profile_url: str) -> str:
    tipo_label = "veterinário(a)" if tipo == "veterinarian" else "clínica"
    body = (
        _h1(f"Perfil aprovado! 🎉")
        + _p(f"Ótima notícia, <strong>{name.split()[0]}</strong>! Seu cadastro como <strong>{tipo_label}</strong> no VetLândia foi <strong style='color:{_BRAND_COLOR};'>aprovado</strong>.")
        + _p("Seu perfil já está visível para tutores e você pode começar a receber avaliações e recomendações.")
        + _btn("Ver meu perfil", profile_url)
    )
    return _wrap(body, preview="Seu perfil foi aprovado! Acesse e veja como está.")


def tpl_reprovacao(name: str, tipo: str) -> str:
    tipo_label = "veterinário(a)" if tipo == "veterinarian" else "clínica"
    body = (
        _h1("Cadastro não aprovado")
        + _p(f"Olá, <strong>{name.split()[0]}</strong>.")
        + _p(f"Infelizmente, seu cadastro como <strong>{tipo_label}</strong> não foi aprovado nesta análise.")
        + _p("Isso pode ocorrer por informações incompletas, inconsistentes ou que não atendem aos critérios da plataforma. Entre em contato com nosso suporte para mais detalhes.")
        + _btn("Falar com o suporte", f"mailto:{settings.SMTP_USER}")
    )
    return _wrap(body, preview="Informações sobre seu cadastro no VetLândia.")


def tpl_nova_avaliacao(
    reviewee_name: str,
    author_name: str,
    rating: int,
    comment: str | None,
    profile_url: str,
) -> str:
    stars = "⭐" * rating
    body = (
        _h1("Você recebeu uma nova avaliação!")
        + _p(f"<strong>{author_name}</strong> deixou uma avaliação no seu perfil:")
        + _quote(f"{stars} &nbsp; {comment or '(sem comentário)'}")
        + _p("A avaliação passará por moderação antes de ser publicada. Após aprovada, ficará visível no seu perfil.")
        + _btn("Ver meu perfil", profile_url)
    )
    return _wrap(body, preview=f"{author_name} avaliou seu perfil com {rating} estrela(s).")


def tpl_avaliacao_publicada(author_name: str, reviewee_name: str, profile_url: str) -> str:
    body = (
        _h1("Sua avaliação foi publicada!")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>!")
        + _p(f"Sua avaliação sobre <strong>{reviewee_name}</strong> foi aprovada e já está visível no perfil público.")
        + _btn("Ver perfil", profile_url)
    )
    return _wrap(body, preview=f"Sua avaliação sobre {reviewee_name} foi publicada.")


def tpl_nova_recomendacao(
    target_name: str,
    author_name: str,
    content: str,
    profile_url: str,
) -> str:
    body = (
        _h1("Você recebeu uma nova recomendação!")
        + _p(f"<strong>{author_name}</strong> escreveu sobre você:")
        + _quote(content)
        + _p("A recomendação passará por moderação antes de ser publicada. Após aprovada, ficará visível no seu perfil.")
        + _btn("Ver meu perfil", profile_url)
    )
    return _wrap(body, preview=f"{author_name} escreveu uma recomendação sobre você.")


def tpl_recomendacao_publicada(author_name: str, target_name: str, profile_url: str) -> str:
    body = (
        _h1("Sua recomendação foi publicada!")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>!")
        + _p(f"Sua recomendação sobre <strong>{target_name}</strong> foi aprovada e já está visível no perfil público.")
        + _btn("Ver perfil", profile_url)
    )
    return _wrap(body, preview=f"Sua recomendação sobre {target_name} foi publicada.")
