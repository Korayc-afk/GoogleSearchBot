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
    logger.info("=" * 50)
    logger.info(f"⏰ Zamanlanmış arama tetiklendi: {datetime.utcnow()}")
    logger.info("=" * 50)
    
    db = SessionLocal()
    try:
        settings = db.query(SearchSettings).filter(SearchSettings.enabled == True).first()
        
        if settings:
            logger.info(f"📋 Ayar bulundu: {settings.search_query} - {settings.location} (Interval: {settings.interval_hours} saat)")
            
            # Çoklu arama kelimesi desteği (virgülle ayrılmış)
            queries = [q.strip() for q in settings.search_query.split(',') if q.strip()]
            logger.info(f"🔍 {len(queries)} kelime için arama yapılacak")
            
            for query in queries:
                logger.info(f"🔎 Arama başlatılıyor: '{query}'")
                # Geçici settings objesi oluştur
                temp_settings = SearchSettings(
                    id=settings.id,
                    search_query=query,
                    location=settings.location,
                    enabled=settings.enabled,
                    interval_hours=settings.interval_hours
                )
                perform_search(db, temp_settings)
                logger.info(f"✅ '{query}' araması tamamlandı")
        else:
            logger.warning("⚠️ Aktif arama ayarı bulunamadı")
    except Exception as e:
        logger.error(f"❌ Zamanlanmış arama hatası: {str(e)}", exc_info=True)
    finally:
        db.close()
        logger.info("=" * 50)


def start_scheduler():
    """Scheduler'ı başlatır - veritabanındaki interval_hours ayarına göre"""
    if scheduler.running:
        logger.warning("Scheduler zaten çalışıyor")
        return
    
    # Veritabanından interval_hours ayarını al
    db = SessionLocal()
    try:
        settings = db.query(SearchSettings).filter(SearchSettings.enabled == True).first()
        
        # Son arama zamanını kontrol et
        last_result = db.query(SearchResult).order_by(SearchResult.search_date.desc()).first()
        last_search_date = last_result.search_date if last_result else None
        
        if settings:
            interval_hours = settings.interval_hours
            
            # Eğer son arama varsa, bir sonraki çalışma zamanını hesapla
            start_date = None
            if last_search_date:
                # Son aramadan itibaren interval kadar sonra
                start_date = last_search_date + timedelta(hours=interval_hours)
                # Eğer geçmişte kaldıysa, şimdiden başlat
                if start_date < datetime.utcnow():
                    start_date = datetime.utcnow() + timedelta(minutes=1)  # 1 dakika sonra başlat
                logger.info(f"📅 Son arama: {last_search_date}, Bir sonraki: {start_date}")
            
            # Interval'e göre arama job'u ekle
            scheduler.add_job(
                run_scheduled_searches,
                trigger=IntervalTrigger(hours=interval_hours),
                id="search_job",
                replace_existing=True
            )
            
            # Eğer start_date varsa ve gelecekteyse, job'u reschedule et
            if start_date and start_date > datetime.utcnow():
                try:
                    scheduler.reschedule_job("search_job", trigger=IntervalTrigger(hours=interval_hours, start_date=start_date))
                    logger.info(f"⏰ İlk arama zamanı ayarlandı: {start_date}")
                except Exception as e:
                    logger.warning(f"Job reschedule edilirken hata (start_date kullanılamıyor olabilir): {e}")
                    # Alternatif: Eğer son aramadan itibaren interval geçtiyse, hemen çalıştır
                    if last_search_date:
                        time_since_last = (datetime.utcnow() - last_search_date).total_seconds() / 3600
                        if time_since_last >= interval_hours:
                            logger.info(f"⏰ Son aramadan {time_since_last:.1f} saat geçti, hemen arama yapılıyor...")
                            # Hemen bir arama yap
                            import threading
                            threading.Thread(target=run_scheduled_searches, daemon=True).start()
            
            logger.info(f"✅ Scheduler başlatıldı - {interval_hours} saatte bir arama yapılacak")
        else:
            # Varsayılan: 12 saatte bir
            scheduler.add_job(
                run_scheduled_searches,
                trigger=IntervalTrigger(hours=12),
                id="search_job",
                replace_existing=True
            )
            logger.info("✅ Scheduler başlatıldı - Varsayılan: 12 saatte bir arama yapılacak")
    except Exception as e:
        logger.error(f"❌ Scheduler başlatılırken hata: {e}", exc_info=True)
        # Hata durumunda varsayılan değer
        scheduler.add_job(
            run_scheduled_searches,
            trigger=IntervalTrigger(hours=12),
            id="search_job",
            replace_existing=True
        )
    finally:
        db.close()
    
    # Her gün saat 09:00'da günlük özet email gönder
    scheduler.add_job(
        run_daily_summary,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_summary",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"🚀 Scheduler başlatıldı - Running: {scheduler.running}")


def stop_scheduler():
    """Scheduler'ı durdurur"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler durduruldu")


def update_scheduler_interval(interval_hours: int):
    """Scheduler interval'ını günceller"""
    logger.info(f"🔄 Scheduler interval güncelleniyor: {interval_hours} saat")
    
    # Mevcut job'u kaldır
    if scheduler.running:
        try:
            scheduler.remove_job("search_job")
            logger.info("🗑️ Eski job kaldırıldı")
        except Exception as e:
            logger.warning(f"Eski job kaldırılırken hata: {e}")
    
    # Son arama zamanını kontrol et
    db = SessionLocal()
    try:
        last_result = db.query(SearchResult).order_by(SearchResult.search_date.desc()).first()
        last_search_date = last_result.search_date if last_result else None
        
        # Eğer son arama varsa, bir sonraki çalışma zamanını hesapla
        start_date = None
        if last_search_date:
            # Son aramadan itibaren interval kadar sonra
            start_date = last_search_date + timedelta(hours=interval_hours)
            # Eğer geçmişte kaldıysa, şimdiden başlat
            if start_date < datetime.utcnow():
                start_date = datetime.utcnow() + timedelta(minutes=1)  # 1 dakika sonra başlat
            logger.info(f"📅 Son arama: {last_search_date}, Bir sonraki: {start_date}")
        else:
            # İlk arama için 1 dakika sonra başlat
            start_date = datetime.utcnow() + timedelta(minutes=1)
            logger.info(f"📅 İlk arama için: {start_date}")
    finally:
        db.close()
    
    # Yeni interval ile job ekle
    scheduler.add_job(
        run_scheduled_searches,
        trigger=IntervalTrigger(hours=interval_hours),
        id="search_job",
        replace_existing=True
    )
    
    # Eğer start_date varsa ve gelecekteyse, job'u reschedule et
    if start_date and start_date > datetime.utcnow():
        try:
            scheduler.reschedule_job("search_job", trigger=IntervalTrigger(hours=interval_hours, start_date=start_date))
            logger.info(f"⏰ Bir sonraki arama zamanı ayarlandı: {start_date}")
        except Exception as e:
            logger.warning(f"Job reschedule edilirken hata (start_date kullanılamıyor olabilir): {e}")
            # Alternatif: Eğer son aramadan itibaren interval geçtiyse, hemen çalıştır
            if last_search_date:
                time_since_last = (datetime.utcnow() - last_search_date).total_seconds() / 3600
                if time_since_last >= interval_hours:
                    logger.info(f"⏰ Son aramadan {time_since_last:.1f} saat geçti, hemen arama yapılıyor...")
                    # Hemen bir arama yap
                    import threading
                    threading.Thread(target=run_scheduled_searches, daemon=True).start()
    
    # Eğer scheduler çalışmıyorsa başlat
    if not scheduler.running:
        scheduler.start()
        logger.info("🚀 Scheduler başlatıldı")
    
    logger.info(f"✅ Scheduler güncellendi - {interval_hours} saatte bir arama yapılacak")

