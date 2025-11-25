import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import SessionLocal, SearchSettings, SearchResult, SearchLink
from app.serpapi_client import SerpApiClient
from app.email_service import email_service

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
        
        # Pozisyon değişikliklerini kontrol et ve email gönder
        check_position_changes(db, links)
        
    except Exception as e:
        logger.error(f"Arama sırasında hata: {str(e)}")
        db.rollback()


def check_position_changes(db: Session, new_links: list):
    """Pozisyon değişikliklerini kontrol et ve email gönder"""
    try:
        # Son aramadan önceki son aramayı bul
        last_result = db.query(SearchResult)\
            .order_by(SearchResult.search_date.desc())\
            .offset(1)\
            .first()
        
        if not last_result:
            return
        
        # Önceki aramadaki linkleri al
        old_links = db.query(SearchLink)\
            .filter(SearchLink.search_result_id == last_result.id)\
            .all()
        
        old_positions = {link.url: link.position for link in old_links}
        
        # Yeni linklerle karşılaştır
        for new_link_data in new_links:
            url = new_link_data["url"]
            new_position = new_link_data["position"]
            
            if url in old_positions:
                old_position = old_positions[url]
                change = new_position - old_position
                
                # Önemli değişiklik varsa email gönder
                if abs(change) >= 3:  # 3+ pozisyon değişikliği
                    asyncio.create_task(
                        email_service.send_position_change_alert(
                            url=url,
                            domain=new_link_data.get("domain", ""),
                            old_position=old_position,
                            new_position=new_position,
                            change=change
                        )
                    )
                
                # Kritik düşüş (5+ pozisyon)
                if change >= 5:
                    asyncio.create_task(
                        email_service.send_critical_drop_alert(
                            url=url,
                            domain=new_link_data.get("domain", ""),
                            old_position=old_position,
                            new_position=new_position
                        )
                    )
    except Exception as e:
        logger.error(f"Pozisyon kontrolü hatası: {str(e)}")


async def send_daily_summary_email():
    """Günlük özet email gönder"""
    db = SessionLocal()
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Dünkü aramaları al
        results = db.query(SearchResult)\
            .filter(SearchResult.search_date >= yesterday_start)\
            .filter(SearchResult.search_date <= yesterday_end)\
            .all()
        
        if not results:
            return
        
        # Top linkleri al
        from app.api.search import get_link_stats_for_period
        top_links = get_link_stats_for_period(
            db, yesterday_start, yesterday_end, limit=10
        )
        
        # Email gönder
        await email_service.send_daily_summary(
            total_searches=len(results),
            unique_links=len(set(link.url for result in results for link in result.links)),
            top_links=[link.dict() if hasattr(link, 'dict') else link for link in top_links],
            date=yesterday.strftime("%Y-%m-%d")
        )
    except Exception as e:
        logger.error(f"Günlük özet email hatası: {str(e)}")
    finally:
        db.close()


def run_daily_summary():
    """Günlük özet email gönder (synchronous wrapper)"""
    asyncio.run(send_daily_summary_email())


def run_scheduled_searches():
    """Tüm aktif ayarlar için arama yapar (çoklu kelime desteği ile)"""
    db = SessionLocal()
    try:
        settings = db.query(SearchSettings).filter(SearchSettings.enabled == True).first()
        
        if settings:
            # Çoklu arama kelimesi desteği (virgülle ayrılmış)
            queries = [q.strip() for q in settings.search_query.split(',') if q.strip()]
            
            for query in queries:
                # Geçici settings objesi oluştur
                temp_settings = SearchSettings(
                    id=settings.id,
                    search_query=query,
                    location=settings.location,
                    enabled=settings.enabled,
                    interval_hours=settings.interval_hours
                )
                perform_search(db, temp_settings)
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
    
    # Her saat başı çalışacak şekilde ayarla (24 saatte 24 kez)
    scheduler.add_job(
        run_scheduled_searches,
        trigger=CronTrigger(minute=0),  # Her saat başı (0. dakikada)
        id="search_job",
        replace_existing=True
    )
    
    # Her gün saat 09:00'da günlük özet email gönder
    scheduler.add_job(
        run_daily_summary,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_summary",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler başlatıldı - Her saat başı arama yapılacak (24 saatte 24 kez), günlük özet 09:00'da gönderilecek")


def stop_scheduler():
    """Scheduler'ı durdurur"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler durduruldu")


def update_scheduler_interval(interval_hours: int):
    """Scheduler interval'ını günceller (kullanılmıyor - artık her saat başı çalışıyor)"""
    # Not: Artık her saat başı çalışacak şekilde ayarlandı
    # Bu fonksiyon geriye dönük uyumluluk için bırakıldı
    logger.warning("update_scheduler_interval kullanılmıyor - scheduler her saat başı çalışıyor")

