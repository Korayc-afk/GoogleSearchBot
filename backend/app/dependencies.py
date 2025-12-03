from fastapi import Query
from app.database import get_db as _get_db

def get_site_id(site_id: str = Query("default", description="Site ID")) -> str:
    """Site ID'yi query parametresinden alır"""
    return site_id

def get_db(site_id: str = Query("default", description="Site ID")):
    """Site ID'ye göre database session döndürür"""
    for db in _get_db(site_id):
        yield db

