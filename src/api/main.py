"""
FastAPI application for XFactor Bot Control Panel.
XFactor Bot - AI-Powered Automated Trading System
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.config.settings import get_settings
from src.monitoring.metrics import MetricsCollector


# Global instances (initialized in lifespan)
metrics = MetricsCollector()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    logger.info("🚀 Starting XFactor Bot API...")
    
    # Startup
    # TODO: Initialize connections here
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down XFactor Bot API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="XFactor Bot API",
        description="AI-Powered Automated Trading System - Control Panel API",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:9876",
            "http://localhost:9877",
            "http://127.0.0.1:9876",
            "http://foresight.nvidia.com:9876",
            "https://foresight.nvidia.com:9876",
            "*",  # Allow all origins for easier development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from src.api.routes import config, positions, orders, risk, news, admin, bots, ai, integrations, commodities, crypto, fees
    
    app.include_router(config.router, prefix="/api/config", tags=["Config"])
    app.include_router(positions.router, prefix="/api/positions", tags=["Positions"])
    app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
    app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])
    app.include_router(news.router, prefix="/api/news", tags=["News"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
    app.include_router(bots.router, prefix="/api/bots", tags=["Bots"])
    app.include_router(ai.router, prefix="/api", tags=["AI Assistant"])
    app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
    app.include_router(commodities.router, prefix="/api/commodities", tags=["Commodities"])
    app.include_router(crypto.router, prefix="/api/crypto", tags=["Crypto"])
    app.include_router(fees.router, prefix="/api/fees", tags=["Fees"])
    
    @app.get("/api")
    async def api_root():
        return {"status": "ok", "name": "XFactor Bot", "version": "0.1.0", "description": "AI-Powered Automated Trading System"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/metrics")
    async def prometheus_metrics():
        return Response(
            content=metrics.get_metrics(),
            media_type=metrics.get_content_type(),
        )
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await websocket.accept()
        logger.info("WebSocket client connected")
        
        try:
            while True:
                # Receive messages from client
                data = await websocket.receive_json()
                
                # Handle subscription requests
                if data.get("type") == "subscribe":
                    channel = data.get("channel")
                    logger.debug(f"Client subscribed to {channel}")
                    await websocket.send_json({"type": "subscribed", "channel": channel})
                
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    # Serve static frontend files
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        # Mount static assets
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
        
        # Serve index.html for root
        @app.get("/")
        async def serve_root():
            index_file = frontend_dist / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file), media_type="text/html")
            return {"error": "Frontend not built"}
        
        # Serve index.html for all non-API routes (SPA fallback)
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Don't intercept API, health, metrics, or ws routes
            if full_path.startswith(("api", "health", "metrics", "ws", "docs", "openapi.json", "redoc")):
                return {"error": "Not found", "path": full_path}
            
            index_file = frontend_dist / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file), media_type="text/html")
            return {"error": "Frontend not built"}
        
        logger.info(f"📁 Serving frontend from {frontend_dist}")
    else:
        logger.warning(f"⚠️ Frontend dist not found at {frontend_dist}")
        
        @app.get("/")
        async def root_no_frontend():
            return {"status": "ok", "name": "XFactor Bot", "version": "0.1.0", "description": "AI-Powered Automated Trading System", "note": "Frontend not deployed"}
    
    return app


# Create app instance
app = create_app()

