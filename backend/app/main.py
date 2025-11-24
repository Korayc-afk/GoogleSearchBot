from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import init_db
from app.api import search, settings
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

# API routes
app.include_router(search.router)
app.include_router(settings.router)

# Frontend static files (production için)
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.exists(frontend_path):
    # Static dosyalar için
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Root path için index.html
    @app.get("/")
    async def read_root():
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}
    
    # SPA için tüm route'ları index.html'e yönlendir
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API route'ları hariç
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not found"}


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

