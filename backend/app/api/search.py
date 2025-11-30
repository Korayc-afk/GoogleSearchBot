from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from typing import List
from app.database import get_db, SearchSettings, SearchResult, SearchLink
from app.models import (
    SearchResultResponse, LinkStatsResponse, DailyReportResponse,
    WeeklyReportResponse, MonthlyReportResponse
)
from app.serpapi_client import SerpApiClient
from app.scheduler import perform_search

router = APIRouter(prefix="/api/search", tags=["search"])
serpapi_client = SerpApiClient()


@router.post("/run")
def run_search_now(db: Session = Depends(get_db)):
    """Manuel olarak arama yapar (çoklu kelime desteği ile)"""
    settings = db.query(SearchSettings).filter(SearchSettings.enabled == True).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Aktif arama ayarı bulunamadı")
    
    # Çoklu arama kelimesi desteği
    queries = [q.strip() for q in settings.search_query.split(',') if q.strip()]
    results = []
    
    for query in queries:
        temp_settings = SearchSettings(
            id=settings.id,
            search_query=query,
            location=settings.location,
            enabled=settings.enabled,
            interval_hours=settings.interval_hours
        )
        try:
            perform_search(db, temp_settings)
            results.append({"query": query, "status": "success"})
        except Exception as e:
            results.append({"query": query, "status": "error", "error": str(e)})
    
    return {
        "success": True,
        "message": f"{len(queries)} arama tamamlandı",
        "results": results
    }


@router.get("/results", response_model=List[SearchResultResponse])
def get_search_results(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Arama sonuçlarını listeler"""
    results = db.query(SearchResult)\
        .order_by(SearchResult.search_date.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return results


@router.get("/results/{result_id}", response_model=SearchResultResponse)
def get_search_result(result_id: int, db: Session = Depends(get_db)):
    """Belirli bir arama sonucunu getirir"""
    result = db.query(SearchResult).filter(SearchResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Arama sonucu bulunamadı")
    
    return result


@router.get("/links/stats", response_model=List[LinkStatsResponse])
def get_link_stats(
    days: int = 30,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Link istatistiklerini getirir"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Her link için istatistik hesapla
    links_query = db.query(
        SearchLink.url,
        SearchLink.domain,
        SearchLink.title,
        func.count(SearchLink.id).label("total_appearances"),
        func.min(SearchLink.created_at).label("first_seen"),
        func.max(SearchLink.created_at).label("last_seen"),
        func.avg(SearchLink.position).label("average_position")
    ).filter(
        SearchLink.created_at >= since_date
    ).group_by(
        SearchLink.url, SearchLink.domain, SearchLink.title
    ).order_by(
        func.count(SearchLink.id).desc()
    ).limit(limit)
    
    results = links_query.all()
    
    stats = []
    for row in results:
        # Bu linkin tüm pozisyonlarını al
        positions = db.query(SearchLink.position)\
            .filter(SearchLink.url == row.url)\
            .filter(SearchLink.created_at >= since_date)\
            .all()
        
        # Gün sayısını hesapla
        days_active = (row.last_seen - row.first_seen).days + 1
        
        stats.append(LinkStatsResponse(
            url=row.url,
            domain=row.domain or "",
            title=row.title,
            total_appearances=row.total_appearances,
            days_active=days_active,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            average_position=float(row.average_position) if row.average_position else 0.0,
            positions=[p.position for p in positions]
        ))
    
    return stats


@router.get("/stats")
def get_search_stats(db: Session = Depends(get_db)):
    """Genel arama istatistiklerini getirir"""
    # Toplam arama sayısı
    total_searches = db.query(func.count(SearchResult.id)).scalar() or 0
    
    # Toplam link sayısı
    total_links = db.query(func.count(SearchLink.id)).scalar() or 0
    
    # Benzersiz domain sayısı
    unique_domains = db.query(func.count(func.distinct(SearchLink.domain))).scalar() or 0
    
    # Son 30 gün içindeki link sayısı
    since_date = datetime.utcnow() - timedelta(days=30)
    recent_links = db.query(func.count(SearchLink.id))\
        .filter(SearchLink.created_at >= since_date)\
        .scalar() or 0
    
    # Son 30 gün içindeki benzersiz domain sayısı
    recent_unique_domains = db.query(func.count(func.distinct(SearchLink.domain)))\
        .filter(SearchLink.created_at >= since_date)\
        .scalar() or 0
    
    # Son arama tarihi
    last_search = db.query(SearchResult)\
        .order_by(SearchResult.search_date.desc())\
        .first()
    
    return {
        "total_searches": total_searches,
        "total_links": total_links,
        "unique_domains": unique_domains,
        "recent_links": recent_links,
        "recent_unique_domains": recent_unique_domains,
        "last_search_date": last_search.search_date if last_search else None
    }


@router.get("/reports/daily", response_model=List[DailyReportResponse])
def get_daily_reports(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Günlük raporları getirir"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Her gün için istatistik (SQLite uyumlu)
    daily_stats = db.query(
        func.date(SearchResult.search_date).label("date"),
        func.count(distinct(SearchResult.id)).label("total_searches"),
        func.count(distinct(SearchLink.id)).label("unique_links")
    ).join(
        SearchLink, SearchResult.id == SearchLink.search_result_id
    ).filter(
        SearchResult.search_date >= since_date
    ).group_by(
        func.date(SearchResult.search_date)
    ).order_by(
        func.date(SearchResult.search_date).desc()
    ).all()
    
    reports = []
    for stat in daily_stats:
        # O günün top linklerini al
        if isinstance(stat.date, str):
            stat_date = datetime.strptime(stat.date, "%Y-%m-%d").date()
        else:
            stat_date = stat.date if hasattr(stat.date, 'date') else stat.date
        date_start = datetime.combine(stat_date, datetime.min.time())
        date_end = datetime.combine(stat_date, datetime.max.time())
        
        top_links = get_link_stats_for_period(db, date_start, date_end, limit=10)
        
        reports.append(DailyReportResponse(
            date=stat.date.isoformat(),
            total_searches=stat.total_searches,
            unique_links=stat.unique_links,
            top_links=top_links
        ))
    
    return reports


@router.get("/reports/weekly", response_model=List[WeeklyReportResponse])
def get_weekly_reports(
    weeks: int = 12,
    db: Session = Depends(get_db)
):
    """Haftalık raporları getirir"""
    since_date = datetime.utcnow() - timedelta(weeks=weeks)
    
    # Her hafta için istatistik (SQLite uyumlu)
    weekly_stats = db.query(
        func.strftime("%Y-%W", SearchResult.search_date).label("week_key"),
        func.min(func.date(SearchResult.search_date)).label("date"),
        func.count(distinct(SearchResult.id)).label("total_searches"),
        func.count(distinct(SearchLink.id)).label("unique_links")
    ).join(
        SearchLink, SearchResult.id == SearchLink.search_result_id
    ).filter(
        SearchResult.search_date >= since_date
    ).group_by(
        func.strftime("%Y-%W", SearchResult.search_date)
    ).order_by(
        func.min(SearchResult.search_date).desc()
    ).all()
    
    reports = []
    for stat in weekly_stats:
        # Haftanın başlangıç ve bitiş tarihlerini hesapla
        if isinstance(stat.date, str):
            stat_date = datetime.strptime(stat.date, "%Y-%m-%d").date()
        else:
            stat_date = stat.date if isinstance(stat.date, type(datetime.now().date())) else datetime.strptime(str(stat.date), "%Y-%m-%d").date()
        week_start = datetime.combine(stat_date, datetime.min.time())
        week_start = week_start - timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=6)
        
        top_links = get_link_stats_for_period(db, week_start, week_end, limit=10)
        
        reports.append(WeeklyReportResponse(
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            total_searches=stat.total_searches,
            unique_links=stat.unique_links,
            top_links=top_links
        ))
    
    return reports


@router.get("/reports/monthly", response_model=List[MonthlyReportResponse])
def get_monthly_reports(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Aylık raporları getirir"""
    since_date = datetime.utcnow() - timedelta(days=months * 30)
    
    # Her ay için istatistik
    monthly_stats = db.query(
        func.strftime("%Y-%m", SearchResult.search_date).label("month_year"),
        func.count(distinct(SearchResult.id)).label("total_searches"),
        func.count(distinct(SearchLink.id)).label("unique_links")
    ).join(
        SearchLink, SearchResult.id == SearchLink.search_result_id
    ).filter(
        SearchResult.search_date >= since_date
    ).group_by(
        func.strftime("%Y-%m", SearchResult.search_date)
    ).order_by(
        func.strftime("%Y-%m", SearchResult.search_date).desc()
    ).all()
    
    reports = []
    for stat in monthly_stats:
        year, month = map(int, stat.month_year.split("-"))
        
        # Ayın başlangıç ve bitiş tarihlerini hesapla
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        top_links = get_link_stats_for_period(db, month_start, month_end, limit=10)
        
        reports.append(MonthlyReportResponse(
            month=stat.month_year,
            year=year,
            total_searches=stat.total_searches,
            unique_links=stat.unique_links,
            top_links=top_links
        ))
    
    return reports


def get_link_stats_for_period(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    limit: int = 10
) -> List[LinkStatsResponse]:
    """Belirli bir periyot için link istatistiklerini getirir"""
    links_query = db.query(
        SearchLink.url,
        SearchLink.domain,
        SearchLink.title,
        func.count(SearchLink.id).label("total_appearances"),
        func.min(SearchLink.created_at).label("first_seen"),
        func.max(SearchLink.created_at).label("last_seen"),
        func.avg(SearchLink.position).label("average_position")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= start_date,
        SearchResult.search_date <= end_date
    ).group_by(
        SearchLink.url, SearchLink.domain, SearchLink.title
    ).order_by(
        func.count(SearchLink.id).desc()
    ).limit(limit)
    
    results = links_query.all()
    
    stats = []
    for row in results:
        positions = db.query(SearchLink.position)\
            .join(SearchResult, SearchLink.search_result_id == SearchResult.id)\
            .filter(SearchLink.url == row.url)\
            .filter(SearchResult.search_date >= start_date)\
            .filter(SearchResult.search_date <= end_date)\
            .all()
        
        days_active = (row.last_seen - row.first_seen).days + 1
        
        stats.append(LinkStatsResponse(
            url=row.url,
            domain=row.domain or "",
            title=row.title,
            total_appearances=row.total_appearances,
            days_active=days_active,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            average_position=float(row.average_position) if row.average_position else 0.0,
            positions=[p.position for p in positions]
        ))
    
    return stats


@router.get("/stats")
def get_search_stats(db: Session = Depends(get_db)):
    """Genel arama istatistiklerini getirir"""
    # Toplam arama sayısı
    total_searches = db.query(func.count(SearchResult.id)).scalar() or 0
    
    # Toplam link sayısı
    total_links = db.query(func.count(SearchLink.id)).scalar() or 0
    
    # Benzersiz domain sayısı
    unique_domains = db.query(func.count(func.distinct(SearchLink.domain))).scalar() or 0
    
    # Son 30 gün içindeki link sayısı
    since_date = datetime.utcnow() - timedelta(days=30)
    recent_links = db.query(func.count(SearchLink.id))\
        .filter(SearchLink.created_at >= since_date)\
        .scalar() or 0
    
    # Son 30 gün içindeki benzersiz domain sayısı
    recent_unique_domains = db.query(func.count(func.distinct(SearchLink.domain)))\
        .filter(SearchLink.created_at >= since_date)\
        .scalar() or 0
    
    # Son arama tarihi
    last_search = db.query(SearchResult)\
        .order_by(SearchResult.search_date.desc())\
        .first()
    
    return {
        "total_searches": total_searches,
        "total_links": total_links,
        "unique_domains": unique_domains,
        "recent_links": recent_links,
        "recent_unique_domains": recent_unique_domains,
        "last_search_date": last_search.search_date if last_search else None
    }

