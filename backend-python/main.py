from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from engineio.middleware import Middleware
import asyncio

from app.api.routes import auth, projects
from app.core.config import settings
from app.db.postgres import connect_to_postgres, close_postgres
from app.socket.handlers import register_socket_handlers

fastapi_app = FastAPI(title=settings.PROJECT_NAME)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS] if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@fastapi_app.on_event("startup")
async def startup_event() -> None:
    await connect_to_postgres()

@fastapi_app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_postgres()

fastapi_app.include_router(auth.router, prefix="/auth", tags=["auth"])
fastapi_app.include_router(projects.router, prefix="/projects", tags=["projects"])

# Configure Socket.IO with proper session management
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "*"],
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e6,
    engineio_logger=False,
    logger=False,
    # Ensure polling works properly
    http_session_handler=None,  # Let Socket.IO handle sessions internally
)

# Register handlers
register_socket_handlers(sio)

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
