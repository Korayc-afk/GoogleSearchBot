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

# Frontend static files (production için) - API route'larından ÖNCE mount edilmeli
# Docker'da frontend /app/frontend/dist olarak kopyalanıyor
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
# Eğer yukarıdaki yoksa, Docker path'ini dene
if not os.path.exists(frontend_path):
    frontend_path = "/app/frontend/dist"

# Frontend varsa static dosyaları mount et
if os.path.exists(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Static dosyalar için (CSS, JS, images vb.)
    static_path = os.path.join(frontend_path)
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# API routes - Frontend'den SONRA eklenmeli ki API route'ları öncelikli olsun
app.include_router(search.router)
app.include_router(settings.router)
app.include_router(export.router)
app.include_router(analytics.router)

# Frontend route'ları - EN SON eklenmeli
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
    
    # SPA için tüm route'ları index.html'e yönlendir (API hariç)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API route'ları zaten yukarıda handle ediliyor, buraya gelmemeli
        # Ama yine de kontrol edelim
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return {"error": "Not found"}
        
        # Static dosyalar için
        if full_path.startswith("assets/") or full_path.startswith("static/"):
            return {"error": "Static file not found"}
        
        # Frontend route'u için index.html döndür
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


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Google Search Bot is running"}

