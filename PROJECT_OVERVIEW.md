# 📋 Google Search Bot - Proje Genel Bakış

## 🎯 Proje Nedir?

Google Search Bot, Google arama sonuçlarını otomatik olarak takip eden, pozisyon değişikliklerini izleyen ve raporlayan bir monitoring sistemidir. SerpApi kullanarak Google aramalarını yapar ve sonuçları veritabanında saklar.

## 🏗️ Mimari Yapı

### Teknoloji Stack

**Backend:**
- **FastAPI** - Python web framework
- **SQLite** - Veritabanı (her site için ayrı database)
- **APScheduler** - Zamanlanmış görevler (otomatik arama)
- **SerpApi** - Google arama sonuçlarını çekmek için
- **SQLAlchemy** - ORM (veritabanı yönetimi)

**Frontend:**
- **React** - UI framework
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Recharts** - Grafik ve görselleştirme
- **Axios** - API istekleri
- **date-fns** - Tarih işlemleri

**Deployment:**
- **Docker** - Containerization
- **Coolify** - Hosting ve deployment
- **Nginx** - Reverse proxy (Coolify tarafından yönetilir)

## 🔄 Çalışma Mantığı

### 1. Multi-Site Yapısı

Her firma için ayrı site ve veritabanı:

```
/data/
  ├── default/          → Padisah (ana site)
  │   └── searchbot.db
  ├── gala/
  │   └── searchbot.db
  ├── hit/
  │   └── searchbot.db
  ├── office/
  │   └── searchbot.db
  └── pipo/
      └── searchbot.db
```

**URL Yapısı:**
- `https://yourdomain.com/default` → Padisah
- `https://yourdomain.com/gala` → Gala
- `https://yourdomain.com/hit` → Hit
- `https://yourdomain.com/office` → Office
- `https://yourdomain.com/pipo` → Pipo

### 2. Arama Süreci

#### Manuel Arama (Test Araması)
1. Kullanıcı Settings sayfasından "Test Araması Yap" butonuna tıklar
2. Backend `/api/search/run?site_id={siteId}` endpoint'ini çağırır
3. `perform_search()` fonksiyonu çalışır:
   - SerpApi'ye arama isteği gönderilir
   - Google'dan ilk sayfa sonuçları (10 link) alınır
   - Her link için: URL, başlık, snippet, pozisyon, domain bilgileri çıkarılır
   - Veritabanına kaydedilir:
     - `SearchResult` tablosuna arama kaydı
     - `SearchLink` tablosuna her link kaydı
4. Sonuçlar Dashboard'da görüntülenir

#### Otomatik Arama (Scheduler)
1. APScheduler her X saatte bir (ayarlanabilir) `run_scheduled_searches()` fonksiyonunu çalıştırır
2. Aktif ayarları veritabanından alır
3. Her arama kelimesi için (virgülle ayrılmış) arama yapar
4. Sonuçları veritabanına kaydeder
5. Pozisyon değişikliklerini kontrol eder (email gönderebilir)

### 3. Veri Saklama

#### Veritabanı Yapısı

**`search_settings` Tablosu:**
- `id` - Ayar ID'si
- `search_query` - Aranacak kelime(ler) (virgülle ayrılmış)
- `location` - Arama konumu (varsayılan: "Fatih,Istanbul")
- `enabled` - Bot aktif mi? (true/false)
- `interval_hours` - Arama sıklığı (saat cinsinden)
- `created_at` - Oluşturulma tarihi
- `updated_at` - Güncellenme tarihi

**`search_results` Tablosu:**
- `id` - Sonuç ID'si
- `settings_id` - Hangi ayarlarla yapıldı
- `search_date` - Arama tarihi ve saati
- `total_results` - Toplam sonuç sayısı (Google'dan gelen)

**`search_links` Tablosu:**
- `id` - Link ID'si
- `search_result_id` - Hangi aramaya ait
- `url` - Link URL'i
- `title` - Başlık
- `snippet` - Açıklama
- `position` - Pozisyon (1-10, ilk sayfa)
- `domain` - Domain adı
- `created_at` - Kayıt tarihi

#### Veri Konumu

**Production (Coolify):**
- Her site için: `/app/data/{site_id}/searchbot.db`
- Persistent Storage ile kalıcı hale getirilir
- Container silinse bile veriler korunur

**Local Development:**
- `data/{site_id}/searchbot.db`

### 4. Özellikler

#### Dashboard
- **Otomatik Arama Durumu**: Scheduler durumu, sıklık, sonraki arama zamanı
- **İstatistikler**: Toplam arama, toplam link, benzersiz domain sayıları
- **Son Arama Sonuçları**: En son yapılan aramalar
- **En Çok Görünen Linkler**: Son 7 günde en çok görünen linkler

#### Raporlar
- **Günlük Raporlar**: Her gün için arama istatistikleri
- **Haftalık Raporlar**: Haftalık özetler
- **Aylık Raporlar**: Aylık özetler
- **Excel Export**: Tüm raporları Excel olarak indirme

#### Grafikler
- **Pozisyon Trend Grafiği**: Link pozisyonlarının zaman içindeki değişimi
- **Domain Dağılımı**: Hangi domainlerin ne kadar göründüğü
- **En Çok Görünen Domainler**: Bar chart ile domain görünürlüğü

#### Analitik
- **Rakip Analizi**: Hangi domainler en çok görünüyor, ortalama pozisyonları
- **Filtreleme**: Domain, URL, pozisyon, tarih aralığına göre filtreleme

#### Ayarlar
- **Arama Ayarları**: 
  - Aranacak kelime(ler) (virgülle ayrılmış çoklu kelime)
  - Arama sıklığı (saat cinsinden)
  - Bot aktif/pasif
- **Genel İstatistikler**: Toplam arama, link, domain sayıları
- **Otomatik Arama Durumu**: Scheduler durumu
- **Son Aramalar**: En son yapılan aramalar listesi

## 🔐 Güvenlik ve İzolasyon

### Site İzolasyonu
- Her site tamamen izole:
  - Ayrı veritabanı dosyası
  - Ayrı ayarlar
  - Ayrı arama sonuçları
  - Aynı SerpApi key'i kullanılır (environment variable'dan)

### Veri Güvenliği
- SQLite dosyaları container içinde saklanır
- Persistent Storage ile kalıcı hale getirilir
- Her site'nin verileri birbirinden tamamen ayrıdır

## 📊 Veri Akışı

```
1. Kullanıcı Arama Ayarlarını Yapar
   ↓
2. Settings → Veritabanına Kaydedilir
   ↓
3. Scheduler Başlatılır (APScheduler)
   ↓
4. Her X Saatte Bir Otomatik Arama
   ↓
5. SerpApi → Google Arama Sonuçları
   ↓
6. Veritabanına Kaydedilir
   ↓
7. Dashboard'da Görüntülenir
   ↓
8. Raporlar ve Grafikler Oluşturulur
```

## 🚀 Deployment Süreci

### Coolify'da Deployment

1. **GitHub Repository**: Kod GitHub'da
2. **Coolify**: Repository'yi bağlar
3. **Docker Build**: Dockerfile ile image oluşturulur
4. **Container**: Image çalıştırılır
5. **Persistent Storage**: `/app/data` klasörü volume olarak mount edilir
6. **Domain**: Domain bağlanır (opsiyonel)
7. **SSL**: Let's Encrypt ile otomatik SSL

### Environment Variables

- `SERPAPI_KEY` - SerpApi anahtarı (tüm siteler için aynı)
- `DATABASE_URL` - Veritabanı URL'i (opsiyonel, varsayılan SQLite)
- `PORT` - Uygulama portu (varsayılan: 8000)

## 📈 Performans ve Ölçeklenebilirlik

### Veri Büyüklüğü
- Her arama: ~10 link
- Her link: ~500 byte
- Günlük veri (12 saatte bir): ~5KB
- Aylık veri: ~150KB
- Yıllık veri: ~1.8MB

**Sonuç:** SQLite yeterli, çok küçük veri hacmi.

### Ölçeklenebilirlik
- Her site için ayrı database → kolay ölçeklenebilir
- SQLite → küçük-orta ölçek için yeterli
- Büyük ölçek için PostgreSQL'e geçilebilir

## 🔧 Bakım ve Yönetim

### Veri Yedekleme
- Coolify'ın backup özelliği kullanılabilir
- Manuel: `docker cp` ile database dosyalarını kopyalama
- Otomatik: Cron job ile düzenli yedekleme

### Loglar
- Backend logları: Container loglarında görüntülenir
- Frontend logları: Browser console'da
- Scheduler logları: Backend loglarında

### Sorun Giderme
- **Veriler görünmüyor**: Persistent Storage kontrol edilmeli
- **Arama çalışmıyor**: SerpApi key kontrol edilmeli
- **Scheduler çalışmıyor**: Container logları kontrol edilmeli

## 🎨 Kullanıcı Arayüzü

### Tema
- **Dark Mode**: Varsayılan dark tema
- **Light Mode**: Toggle ile açılabilir
- **Responsive**: Mobil uyumlu

### Font
- **Anek Latin**: Google Fonts'tan yüklenir
- Modern ve okunabilir

### Logo
- Her sayfada görünür
- `/logo.png` dosyasından serve edilir

## 📝 API Endpoints

### Settings
- `GET /api/settings?site_id={siteId}` - Ayarları getir
- `PUT /api/settings?site_id={siteId}` - Ayarları güncelle
- `GET /api/settings/scheduler-status?site_id={siteId}` - Scheduler durumu

### Search
- `POST /api/search/run?site_id={siteId}` - Manuel arama yap
- `GET /api/search/results?site_id={siteId}` - Arama sonuçlarını listele
- `GET /api/search/stats?site_id={siteId}` - İstatistikleri getir
- `GET /api/search/links/stats?site_id={siteId}` - Link istatistikleri

### Reports
- `GET /api/search/reports/daily?site_id={siteId}` - Günlük raporlar
- `GET /api/search/reports/weekly?site_id={siteId}` - Haftalık raporlar
- `GET /api/search/reports/monthly?site_id={siteId}` - Aylık raporlar

### Analytics
- `GET /api/analytics/position-trend?site_id={siteId}` - Pozisyon trendi
- `GET /api/analytics/domain-distribution?site_id={siteId}` - Domain dağılımı
- `GET /api/analytics/competitor-analysis?site_id={siteId}` - Rakip analizi

### Export
- `GET /api/export/excel/daily?site_id={siteId}` - Günlük Excel
- `GET /api/export/excel/summary?site_id={siteId}` - Özet Excel
- `GET /api/export/excel/position-history?site_id={siteId}` - Pozisyon geçmişi

## 🎯 Kullanım Senaryoları

### Senaryo 1: Yeni Site Ekleme
1. Coolify'da yeni domain ekle (opsiyonel)
2. URL'ye git: `https://yourdomain.com/newsite`
3. Settings'ten arama kelimelerini ayarla
4. Test araması yap
5. Otomatik arama başlar

### Senaryo 2: Pozisyon Takibi
1. Dashboard'u aç
2. "En Çok Görünen Linkler" bölümüne bak
3. Grafikler sayfasından pozisyon trendini gör
4. Excel export ile detaylı rapor al

### Senaryo 3: Rakip Analizi
1. Analitik sayfasına git
2. "Rakip Analizi" bölümüne bak
3. Hangi domainlerin en çok göründüğünü gör
4. Ortalama pozisyonları karşılaştır

## 🔄 Güncelleme Süreci

1. Kod değişikliği yapılır
2. GitHub'a push edilir
3. Coolify otomatik olarak:
   - Yeni kodu çeker
   - Docker image'ı rebuild eder
   - Container'ı yeniden başlatır
4. Veriler korunur (Persistent Storage sayesinde)

## 📚 Dosya Yapısı

```
googleSearchBot/
├── backend/
│   ├── app/
│   │   ├── api/          → API endpoint'leri
│   │   ├── database.py   → Veritabanı modelleri
│   │   ├── main.py       → FastAPI uygulaması
│   │   ├── scheduler.py  → Otomatik arama
│   │   └── serpapi_client.py → SerpApi entegrasyonu
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   → React component'leri
│   │   ├── App.jsx        → Ana uygulama
│   │   └── main.jsx      → Entry point
│   └── public/           → Static dosyalar (logo.png)
├── data/                  → Veritabanı dosyaları (gitignore)
│   ├── default/
│   ├── gala/
│   └── ...
└── Dockerfile             → Ana Dockerfile
```

## ✅ Özet

**Ne Yapıyor?**
- Google arama sonuçlarını otomatik takip ediyor
- Pozisyon değişikliklerini izliyor
- Raporlar ve grafikler oluşturuyor
- Multi-site desteği ile her firma için ayrı takip

**Veriler Nerede?**
- SQLite veritabanı dosyalarında
- Her site için ayrı database: `/app/data/{site_id}/searchbot.db`
- Persistent Storage ile kalıcı

**Nasıl Çalışıyor?**
- SerpApi ile Google'dan sonuçları çekiyor
- Veritabanına kaydediyor
- APScheduler ile otomatik arama yapıyor
- Dashboard'da görselleştiriyor

**Kimler Kullanabilir?**
- SEO takibi yapan firmalar
- Pozisyon değişikliklerini izlemek isteyenler
- Rakiplerini analiz etmek isteyenler
- Çoklu site takibi yapanlar

