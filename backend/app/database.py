from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from typing import Dict

# SQLite database - Multi-site desteği
# Her site için ayrı database dosyası
data_dir = os.path.join(os.path.dirname(__file__), "../../data")
os.makedirs(data_dir, exist_ok=True)

# Engine cache - her site için ayrı engine
_engines: Dict[str, any] = {}
_session_makers: Dict[str, any] = {}

Base = declarative_base()

def get_database_path(site_id: str = "default") -> str:
    """Site ID'ye göre database path'i döndürür"""
    # Site ID'yi güvenli hale getir (sadece alfanumerik ve tire)
    safe_site_id = "".join(c for c in site_id if c.isalnum() or c in ('-', '_')) or "default"
    site_dir = os.path.join(data_dir, safe_site_id)
    os.makedirs(site_dir, exist_ok=True)
    db_path = os.path.join(site_dir, "searchbot.db")
    db_path_normalized = os.path.normpath(db_path).replace("\\", "/")
    return db_path_normalized

def get_engine(site_id: str = "default"):
    """Site ID'ye göre engine döndürür (cache'lenmiş)"""
    if site_id not in _engines:
        db_path = get_database_path(site_id)
        database_url = f"sqlite:///{db_path}"
        _engines[site_id] = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
    return _engines[site_id]

def get_session_maker(site_id: str = "default"):
    """Site ID'ye göre session maker döndürür (cache'lenmiş)"""
    if site_id not in _session_makers:
        engine = get_engine(site_id)
        _session_makers[site_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _session_makers[site_id]

# Varsayılan engine (backward compatibility için)
default_db_path = get_database_path("default")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")
engine = get_engine("default")
SessionLocal = get_session_maker("default")


class SearchSettings(Base):
    __tablename__ = "search_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    search_query = Column(String, nullable=False, default="padişah bet")  # Virgülle ayrılmış çoklu kelime desteği
    location = Column(String, nullable=False, default="Fatih,Istanbul")  # Varsayılan konum (kullanıcıya gösterilmez)
    enabled = Column(Boolean, default=True)
    interval_hours = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_results = relationship("SearchResult", back_populates="settings")


class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    settings_id = Column(Integer, ForeignKey("search_settings.id"))
    search_date = Column(DateTime, default=datetime.utcnow, index=True)
    total_results = Column(Integer, default=0)
    
    # Relationships
    settings = relationship("SearchSettings", back_populates="search_results")
    links = relationship("SearchLink", back_populates="search_result")


class SearchLink(Base):
    __tablename__ = "search_links"
    
    id = Column(Integer, primary_key=True, index=True)
    search_result_id = Column(Integer, ForeignKey("search_results.id"))
    url = Column(String, nullable=False, index=True)
    title = Column(String)
    snippet = Column(Text)
    position = Column(Integer)  # 1-10 (ilk sayfadaki pozisyon)
    domain = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    search_result = relationship("SearchResult", back_populates="links")


def init_db(site_id: str = "default"):
    """Initialize database tables for a specific site"""
    engine = get_engine(site_id)
    Base.metadata.create_all(bind=engine)


def get_db(site_id: str = "default"):
    """Database dependency - site_id parametresi ile"""
    SessionLocal = get_session_maker(site_id)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

