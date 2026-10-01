from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from star_wars_rp.api.routers import auth, campaigns, contacts, content, history, player, resolutions
from star_wars_rp.errors import AppError


app = FastAPI(title="Star Wars RP", version="0.1.0")


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(resolutions.router, prefix="/api")
app.include_router(player.router, prefix="/api")
app.include_router(history.router, prefix="/api")
