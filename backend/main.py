"""
RepoGuard AI — FastAPI Backend
Main application entry point.
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown events."""
    logger.info("🛡️  RepoGuard AI backend starting...")
    yield
    logger.info("RepoGuard AI backend shutting down")


app = FastAPI(
    title="RepoGuard AI",
    description="AI-powered security scanner for GitHub repositories",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
except ImportError:
    logger.info("slowapi not installed — rate limiting disabled")

# Import and register routers
from routers.scan import router as scan_router
from routers.fix import router as fix_router

app.include_router(scan_router)
app.include_router(fix_router)

# WebSocket endpoint
from ws import progress as ws_progress


@app.websocket("/ws/scan/{scan_id}")
async def websocket_scan_progress(websocket: WebSocket, scan_id: str):
    """WebSocket endpoint for real-time scan progress."""
    await ws_progress.register(scan_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages (ping/pong)
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_progress.unregister(scan_id, websocket)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "RepoGuard AI",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
