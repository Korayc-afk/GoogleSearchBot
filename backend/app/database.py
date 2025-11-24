from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# SQLite database
# Data dizinini kontrol et ve oluştur
data_dir = os.path.join(os.path.dirname(__file__), "../../data")
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, "searchbot.db")
# SQLite için path'i normalize et (Windows uyumlu)
db_path_normalized = os.path.normpath(db_path).replace("\\", "/")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path_normalized}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SearchSettings(Base):
    __tablename__ = "search_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    search_query = Column(String, nullable=False, default="padişah bet")
    location = Column(String, nullable=False, default="Fatih,Istanbul")  # Fatih,Istanbul veya Istanbul
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


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

