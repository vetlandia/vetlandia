from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.routers import auth, pages

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Confiança para quem cuida. Conhecimento para quem trata.",
)

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
