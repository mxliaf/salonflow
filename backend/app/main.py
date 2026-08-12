from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import agendamentos, auth, servicos, ws
from app.services.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await ws_manager.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API RESTful e WebSocket para o sistema de agendamento de horários do salão SalonFlow",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers customizados
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Erro interno do servidor: {exc!s}"}
    )

# Routers
app.include_router(auth.router)
app.include_router(agendamentos.router)
app.include_router(servicos.router)
app.include_router(ws.router)

@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

