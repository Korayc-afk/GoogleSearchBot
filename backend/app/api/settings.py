from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SearchSettings
from app.models import (
    SearchSettingsResponse, SearchSettingsCreate, SearchSettingsUpdate
)
from app.scheduler import update_scheduler_interval, start_scheduler, stop_scheduler

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SearchSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Mevcut arama ayarlarını getirir"""
    settings = db.query(SearchSettings).first()
    
    if not settings:
        # Varsayılan ayarları oluştur
        settings = SearchSettings(
            search_query="padişah bet",
            location="Fatih,Istanbul",
            enabled=True,
            interval_hours=12
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("", response_model=SearchSettingsResponse)
def update_settings(
    settings_update: SearchSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Arama ayarlarını günceller"""
    settings = db.query(SearchSettings).first()
    
    if not settings:
        # Yeni ayar oluştur
        settings_data = settings_update.dict(exclude_unset=True)
        settings = SearchSettings(
            search_query=settings_data.get("search_query", "padişah bet"),
            location=settings_data.get("location", "Fatih,Istanbul"),
            enabled=settings_data.get("enabled", True),
            interval_hours=settings_data.get("interval_hours", 12)
        )
        db.add(settings)
    else:
        # Mevcut ayarları güncelle
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    # Scheduler'ı güncelle
    if settings.enabled:
        update_scheduler_interval(settings.interval_hours)
    else:
        stop_scheduler()
    
    return settings


@router.post("", response_model=SearchSettingsResponse)
def create_settings(
    settings_create: SearchSettingsCreate,
    db: Session = Depends(get_db)
):
    """Yeni arama ayarı oluşturur"""
    # Mevcut ayar varsa güncelle
    existing = db.query(SearchSettings).first()
    if existing:
        raise HTTPException(status_code=400, detail="Arama ayarı zaten mevcut. PUT endpoint'ini kullanın.")
    
    settings = SearchSettings(**settings_create.dict())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    # Scheduler'ı başlat
    if settings.enabled:
        update_scheduler_interval(settings.interval_hours)
    
    return settings

