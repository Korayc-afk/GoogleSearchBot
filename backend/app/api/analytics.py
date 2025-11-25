from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db, SearchResult, SearchLink, SearchSettings
from app.models import LinkStatsResponse

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/position-trend")
def get_position_trend(
    url: Optional[str] = Query(None, description="Belirli bir URL için trend"),
    days: int = Query(30, description="Kaç günlük veri"),
    db: Session = Depends(get_db)
):
    """Pozisyon trend verilerini getirir"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        func.date(SearchResult.search_date).label("date"),
        SearchLink.url,
        SearchLink.domain,
        func.avg(SearchLink.position).label("avg_position"),
        func.min(SearchLink.position).label("min_position"),
        func.max(SearchLink.position).label("max_position"),
        func.count(SearchLink.id).label("count")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= since_date
    )
    
    if url:
        query = query.filter(SearchLink.url == url)
    
    results = query.group_by(
        func.date(SearchResult.search_date),
        SearchLink.url,
        SearchLink.domain
    ).order_by(
        func.date(SearchResult.search_date).asc()
    ).all()
    
    # Günlere göre grupla
    daily_data = {}
    for row in results:
        date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append({
            "url": row.url,
            "domain": row.domain or "",
            "avg_position": float(row.avg_position),
            "min_position": row.min_position,
            "max_position": row.max_position,
            "count": row.count
        })
    
    return {
        "daily_data": daily_data,
        "summary": {
            "total_days": len(daily_data),
            "total_records": sum(len(v) for v in daily_data.values())
        }
    }


@router.get("/domain-distribution")
def get_domain_distribution(
    days: int = Query(30, description="Kaç günlük veri"),
    limit: int = Query(20, description="Kaç domain gösterilecek"),
    db: Session = Depends(get_db)
):
    """Domain dağılımını getirir"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        SearchLink.domain,
        func.count(SearchLink.id).label("total_links"),
        func.count(distinct(SearchLink.url)).label("unique_urls"),
        func.avg(SearchLink.position).label("avg_position"),
        func.min(SearchLink.position).label("best_position")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= since_date,
        SearchLink.domain.isnot(None),
        SearchLink.domain != ""
    ).group_by(
        SearchLink.domain
    ).order_by(
        func.count(SearchLink.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "domain": row.domain,
            "total_links": row.total_links,
            "unique_urls": row.unique_urls,
            "avg_position": float(row.avg_position) if row.avg_position else 0.0,
            "best_position": row.best_position
        }
        for row in results
    ]


@router.get("/top-movers")
def get_top_movers(
    days: int = Query(7, description="Kaç günlük veri"),
    limit: int = Query(10, description="Kaç sonuç"),
    direction: str = Query("both", description="up, down, veya both"),
    db: Session = Depends(get_db)
):
    """En çok yükselen/düşen linkleri getirir"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # İlk ve son pozisyonları bul
    first_positions = db.query(
        SearchLink.url,
        SearchLink.domain,
        SearchLink.title,
        func.min(SearchResult.search_date).label("first_date"),
        func.min(SearchLink.position).label("first_position")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= since_date
    ).group_by(
        SearchLink.url, SearchLink.domain, SearchLink.title
    ).subquery()
    
    last_positions = db.query(
        SearchLink.url,
        func.max(SearchResult.search_date).label("last_date"),
        func.min(SearchLink.position).label("last_position")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= since_date
    ).group_by(
        SearchLink.url
    ).subquery()
    
    # İlk ve son pozisyonları birleştir
    query = db.query(
        first_positions.c.url,
        first_positions.c.domain,
        first_positions.c.title,
        first_positions.c.first_position,
        last_positions.c.last_position,
        (first_positions.c.first_position - last_positions.c.last_position).label("change")
    ).join(
        last_positions, first_positions.c.url == last_positions.c.url
    )
    
    if direction == "up":
        query = query.filter(first_positions.c.first_position > last_positions.c.last_position)
    elif direction == "down":
        query = query.filter(first_positions.c.first_position < last_positions.c.last_position)
    
    results = query.order_by(
        func.abs((first_positions.c.first_position - last_positions.c.last_position)).desc()
    ).limit(limit).all()
    
    return [
        {
            "url": row.url,
            "domain": row.domain or "",
            "title": row.title or "",
            "first_position": row.first_position,
            "last_position": row.last_position,
            "change": row.change,
            "direction": "up" if row.change > 0 else "down" if row.change < 0 else "stable"
        }
        for row in results
    ]


@router.get("/competitor-analysis")
def get_competitor_analysis(
    days: int = Query(30, description="Kaç günlük veri"),
    db: Session = Depends(get_db)
):
    """Rakip analizi - hangi domainler en çok görünüyor"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        SearchLink.domain,
        func.count(distinct(SearchResult.id)).label("appearances"),
        func.avg(SearchLink.position).label("avg_position"),
        func.min(SearchLink.position).label("best_position"),
        func.max(SearchLink.position).label("worst_position"),
        func.count(distinct(SearchLink.url)).label("unique_urls")
    ).join(
        SearchResult, SearchLink.search_result_id == SearchResult.id
    ).filter(
        SearchResult.search_date >= since_date,
        SearchLink.domain.isnot(None),
        SearchLink.domain != ""
    ).group_by(
        SearchLink.domain
    ).order_by(
        func.count(distinct(SearchResult.id)).desc()
    ).limit(20).all()
    
    return [
        {
            "domain": row.domain,
            "appearances": row.appearances,
            "avg_position": float(row.avg_position) if row.avg_position else 0.0,
            "best_position": row.best_position,
            "worst_position": row.worst_position,
            "unique_urls": row.unique_urls,
            "market_share": 0.0  # Hesaplanacak
        }
        for row in results
    ]


@router.get("/filter-links")
def filter_links(
    domain: Optional[str] = Query(None, description="Domain filtresi"),
    url_contains: Optional[str] = Query(None, description="URL içinde geçen kelime"),
    min_position: Optional[int] = Query(None, description="Minimum pozisyon"),
    max_position: Optional[int] = Query(None, description="Maximum pozisyon"),
    start_date: Optional[str] = Query(None, description="Başlangıç tarihi (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Bitiş tarihi (YYYY-MM-DD)"),
    days: int = Query(30, description="Varsayılan gün sayısı"),
    limit: int = Query(100, description="Maksimum sonuç"),
    db: Session = Depends(get_db)
):
    """Linkleri filtrele"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(SearchLink, SearchResult)\
        .join(SearchResult, SearchLink.search_result_id == SearchResult.id)\
        .filter(SearchResult.search_date >= since_date)
    
    if domain:
        query = query.filter(SearchLink.domain.contains(domain))
    
    if url_contains:
        query = query.filter(SearchLink.url.contains(url_contains))
    
    if min_position:
        query = query.filter(SearchLink.position >= min_position)
    
    if max_position:
        query = query.filter(SearchLink.position <= max_position)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(SearchResult.search_date >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end + timedelta(days=1)  # Günün sonuna kadar
            query = query.filter(SearchResult.search_date < end)
        except:
            pass
    
    results = query.order_by(SearchResult.search_date.desc()).limit(limit).all()
    
    return [
        {
            "id": link.id,
            "url": link.url,
            "domain": link.domain or "",
            "title": link.title or "",
            "position": link.position,
            "snippet": link.snippet or "",
            "search_date": result.search_date.isoformat(),
            "total_results": result.total_results
        }
        for link, result in results
    ]



