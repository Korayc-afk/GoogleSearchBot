from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import logging
from app.database import init_db
from app.api import search, settings, export, analytics
from app.scheduler import start_scheduler

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yönetimi"""
    # Startup
    try:
        logger.info("=" * 60)
        logger.info("🚀 STARTUP EVENT BAŞLADI")
        logger.info("=" * 60)
        logger.info("🚀 Starting Google Search Bot...")
        
        # Veritabanını başlat
        logger.info("📦 Veritabanı başlatılıyor...")
        init_db()
        logger.info("✅ Database initialized")
        
        # Scheduler'ı başlat
        logger.info("⏰ Scheduler başlatılıyor...")
        start_scheduler()
        logger.info("✅ Scheduler started")
        
        logger.info("=" * 60)
        logger.info("✅ Google Search Bot başlatıldı!")
        logger.info("=" * 60)
        print("✅ Google Search Bot başlatıldı!")
    except Exception as e:
        logger.error(f"❌ Startup event hatası: {e}", exc_info=True)
        print(f"❌ Startup event hatası: {e}")
    
    yield
    
    # Shutdown
    try:
        logger.info("🛑 Shutdown event başladı...")
        from app.scheduler import stop_scheduler
        stop_scheduler()
        logger.info("🛑 Google Search Bot durduruldu!")
        print("🛑 Google Search Bot durduruldu!")
    except Exception as e:
        logger.error(f"❌ Shutdown event hatası: {e}", exc_info=True)


app = FastAPI(
    title="Google Search Bot API",
    description="SerpApi ile Google arama botu ve dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler ekleyin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} -> {response.status_code}")
    return response

# Frontend path'i belirle
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if not os.path.exists(frontend_path):
    frontend_path = "/app/frontend/dist"

# Health check endpoint - EN ÖNCE tanımlanmalı (API route'larından önce)
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    logger.info("🔍 /api/health endpoint called")
    frontend_check = os.path.exists(frontend_path)
    index_check = os.path.exists(os.path.join(frontend_path, "index.html")) if frontend_check else False
    
    logger.info(f"📁 Frontend path: {frontend_path}")
    logger.info(f"📁 Frontend exists: {frontend_check}")
    logger.info(f"📄 Index exists: {index_check}")
    
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
    # Assets klasörü (JS, CSS dosyaları)
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Logo ve diğer public dosyalar için özel route
    logo_path = os.path.join(frontend_path, "logo.png")
    if os.path.exists(logo_path):
        @app.get("/logo.png")
        async def get_logo():
            return FileResponse(logo_path)

# Root route ve Frontend SPA routing - EN SON eklenmeli
if os.path.exists(frontend_path):
    index_path = os.path.join(frontend_path, "index.html")
    
    # Geçerli site ID'leri tanımla
    VALID_SITE_IDS = ['default', 'gala', 'hit', 'office', 'pipo', 'padisah']
    
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
    
    # Sadece geçerli site ID'leri için frontend serve et
    
    @app.get("/{site_id}")
    async def serve_site(site_id: str):
        """Sadece geçerli site ID'leri için frontend serve eder"""
        # Geçerli site ID kontrolü
        if site_id not in VALID_SITE_IDS:
            return JSONResponse(
                status_code=404,
                content={"error": "Site not found", "path": site_id, "valid_sites": VALID_SITE_IDS}
            )
        
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return JSONResponse(
            status_code=404,
            content={"error": "Frontend not found"}
        )
    
    # SPA için catch-all route - sadece geçerli site ID'leri için
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        # API route'ları buraya gelmemeli
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            return JSONResponse(
                status_code=404,
                content={"error": "Not found", "path": full_path}
            )
        
        # Static dosyalar için özel kontrol
        if (full_path.startswith('assets/') or
            full_path.endswith('.png') or
            full_path.endswith('.jpg') or
            full_path.endswith('.ico') or
            full_path.endswith('.svg') or
            full_path.endswith('.js') or
            full_path.endswith('.css')):
            # Static dosyalar zaten mount edildi, buraya gelmemeli
            return JSONResponse(
                status_code=404,
                content={"error": "Static file not found", "path": full_path}
            )
        
        # Path'i parçala
        path_parts = full_path.split('/')
        site_id = path_parts[0] if path_parts else ''
        
        # Sadece geçerli site ID'leri için frontend serve et
        if site_id in VALID_SITE_IDS:
            if os.path.exists(index_path):
                return FileResponse(index_path)
        
        # Geçersiz path için 404
        return JSONResponse(
            status_code=404,
            content={"error": "Page not found", "path": full_path, "valid_sites": VALID_SITE_IDS}
        )
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



