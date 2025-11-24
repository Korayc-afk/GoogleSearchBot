import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal, SearchSettings, SearchResult, SearchLink
from app.serpapi_client import SerpApiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
serpapi_client = SerpApiClient()


def perform_search(db: Session, settings: SearchSettings):
    """Arama yapar ve sonuçları veritabanına kaydeder"""
    try:
        logger.info(f"Arama başlatılıyor: {settings.search_query} - {settings.location}")
        
        # SerpApi ile arama yap
        search_data = serpapi_client.search(settings.search_query, settings.location)
        
        if not search_data["success"]:
            logger.error(f"Arama hatası: {search_data.get('error')}")
            return
        
        # Linkleri çıkar
        links = serpapi_client.extract_links(search_data)
        
        # Veritabanına kaydet
        search_result = SearchResult(
            settings_id=settings.id,
            search_date=datetime.utcnow(),
            total_results=search_data.get("total_results", 0)
        )
        db.add(search_result)
        db.flush()  # ID'yi almak için
        
        # Linkleri kaydet
        for link_data in links:
            link = SearchLink(
                search_result_id=search_result.id,
                url=link_data["url"],
                title=link_data.get("title"),
                snippet=link_data.get("snippet"),
                position=link_data["position"],
                domain=link_data.get("domain", "")
            )
            db.add(link)
        
        db.commit()
        logger.info(f"Arama tamamlandı: {len(links)} link kaydedildi")
        
    except Exception as e:
        logger.error(f"Arama sırasında hata: {str(e)}")
        db.rollback()


def run_scheduled_searches():
    """Tüm aktif ayarlar için arama yapar"""
    db = SessionLocal()
    try:
        settings = db.query(SearchSettings).filter(SearchSettings.enabled == True).first()
        
        if settings:
            perform_search(db, settings)
        else:
            logger.warning("Aktif arama ayarı bulunamadı")
    except Exception as e:
        logger.error(f"Zamanlanmış arama hatası: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Scheduler'ı başlatır"""
    if scheduler.running:
        logger.warning("Scheduler zaten çalışıyor")
        return
    
    # Her 12 saatte bir çalışacak şekilde ayarla
    scheduler.add_job(
        run_scheduled_searches,
        trigger=IntervalTrigger(hours=12),
        id="search_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler başlatıldı - 12 saatte bir arama yapılacak")


def stop_scheduler():
    """Scheduler'ı durdurur"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler durduruldu")


def update_scheduler_interval(interval_hours: int):
    """Scheduler interval'ını günceller"""
    stop_scheduler()
    
    scheduler.add_job(
        run_scheduled_searches,
        trigger=IntervalTrigger(hours=interval_hours),
        id="search_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler güncellendi - {interval_hours} saatte bir arama yapılacak")

