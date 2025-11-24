from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import init_db
from app.api import search, settings, export, analytics
from app.scheduler import start_scheduler

app = FastAPI(
    title="Google Search Bot API",
    description="SerpApi ile Google arama botu ve dashboard",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler ekleyin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend path'i belirle
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if not os.path.exists(frontend_path):
    frontend_path = "/app/frontend/dist"

# Health check endpoint - EN ÖNCE tanımlanmalı (API route'larından önce)
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    frontend_check = os.path.exists(frontend_path)
    index_check = os.path.exists(os.path.join(frontend_path, "index.html")) if frontend_check else False
    
    return {
        "status": "ok",
        "message": "Google Search Bot is running",
        "frontend_path": frontend_path,
        "frontend_exists": frontend_check,
        "index_exists": index_check
    }

# API routes - Health'den SONRA, frontend'den ÖNCE
app.include_router(search.router)
app.include_router(settings.router)
app.include_router(export.router)
app.include_router(analytics.router)

# Frontend static files - API route'larından SONRA mount et
if os.path.exists(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Root route ve Frontend SPA routing - EN SON eklenmeli
if os.path.exists(frontend_path):
    index_path = os.path.join(frontend_path, "index.html")
    
    @app.get("/")
    async def read_root():
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {
            "message": "Google Search Bot API",
            "docs": "/docs",
            "health": "/api/health",
            "frontend": "Frontend index.html not found"
        }
    
    # SPA için catch-all route - API route'larından SONRA olmalı
    # Bu route sadece API route'ları match edilmediğinde çalışır
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API, docs, openapi route'ları zaten yukarıda handle edildi
        # Static dosyalar da mount edildi
        # Geri kalan her şey frontend'e yönlendir
        
        # Eğer buraya geldiyse, frontend route'u demektir
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {
            "error": "Frontend not found",
            "api": "/api/health",
            "docs": "/docs"
        }
else:
    # Frontend yoksa basit bir mesaj döndür
    @app.get("/")
    async def read_root():
        return {
            "message": "Google Search Bot API",
            "docs": "/docs",
            "health": "/api/health",
            "frontend": "Frontend not built yet. Check Dockerfile frontend build step."
        }


@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında çalışır"""
    # Veritabanını başlat
    init_db()
    
    # Scheduler'ı başlat
    start_scheduler()
    print("✅ Google Search Bot başlatıldı!")


@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapatıldığında çalışır"""
    from app.scheduler import stop_scheduler
    stop_scheduler()
    print("🛑 Google Search Bot durduruldu!")

