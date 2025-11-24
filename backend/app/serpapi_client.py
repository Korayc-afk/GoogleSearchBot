import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "bb970a4dea7a4ea4952712cd9bd6d6cb73765f27eee2bcb221bc63c7ba7b6068")
SERPAPI_URL = "https://serpapi.com/search"


class SerpApiClient:
    def __init__(self, api_key: str = SERPAPI_KEY):
        self.api_key = api_key
    
    def search(self, query: str, location: str = "Fatih,Istanbul") -> Dict:
        """
        Google'da arama yapar ve ilk sayfadaki sonuçları döner
        
        Args:
            query: Aranacak kelime
            location: Arama konumu (Fatih,Istanbul veya Istanbul)
        
        Returns:
            Dict: Arama sonuçları
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "hl": "tr",
            "gl": "tr",
            "num": 10  # İlk sayfa için 10 sonuç
        }
        
        # Konum ayarı
        if location:
            if location == "Istanbul" or location == "İstanbul":
                params["location"] = "Istanbul, Turkey"
            else:
                params["location"] = location
        
        try:
            response = requests.get(SERPAPI_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "data": data,
                "organic_results": data.get("organic_results", []),
                "total_results": data.get("search_information", {}).get("total_results", 0),
                "search_time": data.get("search_information", {}).get("time_taken_displayed", 0)
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "organic_results": [],
                "total_results": 0
            }
    
    def extract_links(self, search_data: Dict) -> List[Dict]:
        """
        Arama sonuçlarından linkleri çıkarır
        
        Returns:
            List[Dict]: Link bilgileri (url, title, snippet, position, domain)
        """
        links = []
        organic_results = search_data.get("organic_results", [])
        
        for idx, result in enumerate(organic_results, start=1):
            url = result.get("link", "")
            if not url:
                continue
            
            # Domain çıkar
            domain = self._extract_domain(url)
            
            links.append({
                "url": url,
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "position": idx,
                "domain": domain
            })
        
        return links
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """URL'den domain çıkarır"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # www. kaldır
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""

