from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.routers import auth, pages
from app.routers import admin as admin_router
from app.routers import perfil as perfil_router
from app.routers import reviews as reviews_router
from app.routers import cases as cases_router


class WWWRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        if host.startswith("www."):
            bare = host[4:]
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

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_router.router)
app.include_router(perfil_router.router, prefix="/api/perfil", tags=["perfil"])
app.include_router(reviews_router.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(cases_router.router, prefix="/api/casos-clinicos", tags=["casos"])


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response
