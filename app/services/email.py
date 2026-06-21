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
    payload = {
        "from": settings.EMAIL_FROM,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if settings.EMAIL_BCC:
        payload["bcc"] = [settings.EMAIL_BCC]
    resend.Emails.send(payload)


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


def tpl_reprovacao(name: str, tipo: str, reason: str = "") -> str:
    tipo_label = "veterinário(a)" if tipo == "veterinarian" else "clínica"
    motivo = _quote(reason) if reason else _p("Sua solicitação não está em conformidade com as regras e diretrizes estabelecidas.")
    body = (
        _h1("Cadastro não aprovado")
        + _p(f"Olá, <strong>{name.split()[0]}</strong>.")
        + _p(f"Infelizmente, seu cadastro como <strong>{tipo_label}</strong> não foi aprovado.")
        + motivo
        + _p("Em caso de dúvidas, entre em contato com nosso suporte.")
        + _btn("Falar com o suporte", f"mailto:{settings.EMAIL_BCC}")
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


# ── Templates adicionais ───────────────────────────────────────────────────────

def tpl_confirmacao_avaliacao(author_name: str, reviewee_name: str) -> str:
    body = (
        _h1("Avaliação recebida!")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>! Recebemos sua avaliação sobre <strong>{reviewee_name}</strong>.")
        + _p("Ela passará por moderação e, se aprovada, ficará visível no perfil público em breve.")
        + _btn("Acessar VetLândia", _SITE_URL)
    )
    return _wrap(body, preview=f"Sua avaliação sobre {reviewee_name} foi recebida e está em análise.")


def tpl_avaliacao_publicada_reviewee(reviewee_name: str, rating: int, comment: str | None, profile_url: str) -> str:
    stars = "⭐" * rating
    body = (
        _h1("Uma avaliação no seu perfil foi publicada!")
        + _p(f"Olá, <strong>{reviewee_name.split()[0]}</strong>! Uma avaliação recebida foi aprovada pela moderação e já está visível no seu perfil.")
        + _quote(f"{stars} &nbsp; {comment or '(sem comentário)'}")
        + _btn("Ver meu perfil", profile_url)
    )
    return _wrap(body, preview=f"Nova avaliação publicada no seu perfil — {rating} estrela(s).")


def tpl_avaliacao_rejeitada(author_name: str, reviewee_name: str, reason: str = "") -> str:
    motivo = _quote(reason) if reason else _p("Sua solicitação não está em conformidade com as regras e diretrizes estabelecidas.")
    body = (
        _h1("Avaliação não aprovada")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>.")
        + _p(f"Infelizmente, sua avaliação sobre <strong>{reviewee_name}</strong> não foi aprovada pela moderação.")
        + motivo
        + _btn("Voltar ao VetLândia", _SITE_URL)
    )
    return _wrap(body, preview=f"Sua avaliação sobre {reviewee_name} não foi aprovada.")


def tpl_avaliacao_rejeitada_reviewee(reviewee_name: str, reason: str = "") -> str:
    motivo = _quote(reason) if reason else _p("A avaliação não estava em conformidade com nossas diretrizes.")
    body = (
        _h1("Avaliação recebida não aprovada")
        + _p(f"Olá, <strong>{reviewee_name.split()[0]}</strong>.")
        + _p("Uma avaliação recebida no seu perfil não foi aprovada pela moderação e não aparecerá publicamente.")
        + motivo
        + _btn("Ver meu perfil", _SITE_URL)
    )
    return _wrap(body, preview="Uma avaliação recebida foi reprovada pela moderação.")


def tpl_confirmacao_recomendacao(author_name: str, target_name: str) -> str:
    body = (
        _h1("Recomendação recebida!")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>! Recebemos sua recomendação sobre <strong>{target_name}</strong>.")
        + _p("Ela passará por moderação e, se aprovada, ficará visível no perfil público em breve.")
        + _btn("Acessar VetLândia", _SITE_URL)
    )
    return _wrap(body, preview=f"Sua recomendação sobre {target_name} foi recebida e está em análise.")


def tpl_recomendacao_publicada_target(target_name: str, author_name: str, content: str, profile_url: str) -> str:
    body = (
        _h1("Uma recomendação no seu perfil foi publicada!")
        + _p(f"Olá, <strong>{target_name.split()[0]}</strong>! Uma recomendação sobre você foi aprovada e já está visível no seu perfil.")
        + _quote(content)
        + _btn("Ver meu perfil", profile_url)
    )
    return _wrap(body, preview=f"{author_name} escreveu uma recomendação publicada no seu perfil.")


def tpl_recomendacao_rejeitada(author_name: str, target_name: str, reason: str = "") -> str:
    motivo = _quote(reason) if reason else _p("Sua solicitação não está em conformidade com as regras e diretrizes estabelecidas.")
    body = (
        _h1("Recomendação não aprovada")
        + _p(f"Olá, <strong>{author_name.split()[0]}</strong>.")
        + _p(f"Infelizmente, sua recomendação sobre <strong>{target_name}</strong> não foi aprovada pela moderação.")
        + motivo
        + _btn("Voltar ao VetLândia", _SITE_URL)
    )
    return _wrap(body, preview=f"Sua recomendação sobre {target_name} não foi aprovada.")


def tpl_recomendacao_rejeitada_target(target_name: str, reason: str = "") -> str:
    motivo = _quote(reason) if reason else _p("A recomendação não estava em conformidade com nossas diretrizes.")
    body = (
        _h1("Recomendação recebida não aprovada")
        + _p(f"Olá, <strong>{target_name.split()[0]}</strong>.")
        + _p("Uma recomendação recebida no seu perfil não foi aprovada pela moderação e não aparecerá publicamente.")
        + motivo
        + _btn("Ver meu perfil", _SITE_URL)
    )
    return _wrap(body, preview="Uma recomendação recebida foi reprovada pela moderação.")


def tpl_reset_senha(name: str, reset_url: str) -> str:
    body = (
        _h1("Redefinição de senha")
        + _p(f"Olá, <strong>{name.split()[0]}</strong>.")
        + _p("Recebemos uma solicitação para redefinir a senha da sua conta no VetLândia.")
        + _p("Clique no botão abaixo para criar uma nova senha. O link é válido por <strong>1 hora</strong>.")
        + _btn("Redefinir minha senha", reset_url)
        + _p('Se você não solicitou a redefinição de senha, ignore este e-mail. Sua conta continua segura.')
        + f'<p style="margin:16px 0 0;font-size:0.8rem;color:#9ca3af;">Se o botão não funcionar, copie e cole este link no navegador:<br>'
        f'<a href="{reset_url}" style="color:#0d9488;word-break:break-all;">{reset_url}</a></p>'
    )
    return _wrap(body, preview="Você solicitou a redefinição de senha no VetLândia.")
