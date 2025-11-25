from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db, SearchSettings, SearchResult
from app.models import (
    SearchSettingsResponse, SearchSettingsCreate, SearchSettingsUpdate,
    SchedulerStatusResponse
)
from app.scheduler import update_scheduler_interval, start_scheduler, stop_scheduler, scheduler

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


@router.get("/scheduler-status", response_model=SchedulerStatusResponse)
def get_scheduler_status(db: Session = Depends(get_db)):
    """Scheduler durumunu getirir"""
    settings = db.query(SearchSettings).first()
    
    if not settings:
        return SchedulerStatusResponse(
            is_running=False,
            is_enabled=False,
            interval_hours=12,
            total_scheduled_runs=0
        )
    
    # Scheduler durumu
    is_running = scheduler.running if scheduler else False
    
    # Son arama zamanı
    last_result = db.query(SearchResult).order_by(SearchResult.search_date.desc()).first()
    last_search_date = last_result.search_date if last_result else None
    
    # Bir sonraki çalışma zamanı
    next_run_time = None
    last_run_time = None
    if is_running:
        try:
            job = scheduler.get_job("search_job")
            if job:
                next_run_time = job.next_run_time
                # Son çalışma zamanını hesapla
                if next_run_time and settings.interval_hours:
                    from datetime import timedelta
                    last_run_time = next_run_time - timedelta(hours=settings.interval_hours)
        except:
            pass
    
    # Toplam zamanlanmış çalışma sayısı (tahmini)
    total_runs = 0
    if last_search_date and settings.interval_hours:
        # İlk aramadan bu yana geçen süre / interval
        time_diff = datetime.utcnow() - last_search_date
        total_runs = int(time_diff.total_seconds() / 3600 / settings.interval_hours) + 1
    
    return SchedulerStatusResponse(
        is_running=is_running,
        is_enabled=settings.enabled,
        interval_hours=settings.interval_hours,
        last_run_time=last_run_time,
        next_run_time=next_run_time,
        last_search_date=last_search_date,
        total_scheduled_runs=total_runs
    )


