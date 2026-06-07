from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.routers import auth, pages


class WWWRedirectMiddleware(BaseHTTPMiddleware):
    """Redireciona www.vetlandia.com.br → vetlandia.com.br (301 permanente)."""
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        if host.startswith("www."):
            bare = host[4:]  # remove "www."
            url = request.url
            redirect_url = str(url).replace(f"://{host}", f"://{bare}", 1)
            return RedirectResponse(url=redirect_url, status_code=301)
        return await call_next(request)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Confiança para quem cuida. Conhecimento para quem trata.",
)

app.add_middleware(WWWRedirectMiddleware)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Routers
app.include_router(pages.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
