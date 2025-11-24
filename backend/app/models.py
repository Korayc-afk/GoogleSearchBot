from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Search Settings Models
class SearchSettingsBase(BaseModel):
    search_query: str
    location: str
    enabled: bool = True
    interval_hours: int = 12


class SearchSettingsCreate(SearchSettingsBase):
    pass


class SearchSettingsUpdate(BaseModel):
    search_query: Optional[str] = None
    location: Optional[str] = None
    enabled: Optional[bool] = None
    interval_hours: Optional[int] = None


class SearchSettingsResponse(SearchSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Result Models
class SearchLinkResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    snippet: Optional[str]
    position: int
    domain: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchResultResponse(BaseModel):
    id: int
    search_date: datetime
    total_results: int
    links: List[SearchLinkResponse]
    
    class Config:
        from_attributes = True


# Report Models
class LinkStatsResponse(BaseModel):
    url: str
    domain: str
    title: Optional[str]
    total_appearances: int
    days_active: int
    first_seen: datetime
    last_seen: datetime
    average_position: float
    positions: List[int]


class DailyReportResponse(BaseModel):
    date: str
    total_searches: int
    unique_links: int
    top_links: List[LinkStatsResponse]


class WeeklyReportResponse(BaseModel):
    week_start: str
    week_end: str
    total_searches: int
    unique_links: int
    top_links: List[LinkStatsResponse]


class MonthlyReportResponse(BaseModel):
    month: str
    year: int
    total_searches: int
    unique_links: int
    top_links: List[LinkStatsResponse]


# API Response Models
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

