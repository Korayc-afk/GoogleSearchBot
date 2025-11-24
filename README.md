# 🔍 Google Search Bot

SerpApi kullanarak Google aramalarını otomatik olarak yapan, sonuçları kaydeden ve detaylı raporlar sunan bir bot ve dashboard sistemi.

## ✨ Özellikler

- 🔄 **Otomatik Arama**: 12 saatte bir (veya özelleştirilebilir) otomatik Google araması
- 📊 **Dashboard**: Gerçek zamanlı istatistikler ve sonuçlar
- 📈 **Raporlama**: Günlük, haftalık ve aylık detaylı raporlar
- 🔗 **Link Takibi**: İlk sayfadaki linklerin pozisyon, görünme sayısı ve aktif gün takibi
- ⚙️ **Ayarlar**: Dashboard'dan arama kelimesi, konum ve interval ayarları
- 🌙 **Dark Mode**: Modern dark mode desteği
- 📊 **Grafikler**: Pozisyon trend, domain dağılım grafikleri
- 📧 **Email Bildirimleri**: Pozisyon değişiklikleri ve günlük özet email'leri
- 🔍 **Gelişmiş Filtreleme**: Domain, URL, tarih aralığı filtreleme
- 📈 **Analitik**: Rakip analizi, en çok hareket eden linkler
- 📥 **Excel Export**: Günlük pozisyonlar, özet ve pozisyon geçmişi Excel export
- 🔢 **Çoklu Arama**: Virgülle ayrılmış birden fazla kelime takibi
- 🐳 **Docker Desteği**: Coolify ve VPS için hazır

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+ (frontend için)
- Docker (opsiyonel)

### Yerel Geliştirme

1. **Backend'i başlatın:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend'i başlatın:**

```bash
cd frontend
npm install
npm run dev
```

3. Tarayıcıda `http://localhost:3000` adresine gidin.

### Docker ile Kurulum

```bash
docker-compose up -d
```

Uygulama `http://localhost:8000` adresinde çalışacaktır.

### Coolify ile Kurulum

1. Coolify'da yeni bir uygulama oluşturun
2. Git repository'nizi bağlayın
3. Build komutu: `cd backend && pip install -r requirements.txt`
4. Run komutu: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Environment variables:
   - `SERPAPI_KEY`: SerpApi API anahtarınız
   - `DATABASE_URL`: (Opsiyonel) PostgreSQL için, yoksa SQLite kullanılır

## 📖 Kullanım

### İlk Kurulum

1. Dashboard'a gidin
2. **Ayarlar** sekmesine tıklayın
3. Arama kelimesini, konumu ve interval'ı ayarlayın
4. "Ayarları Kaydet" butonuna tıklayın
5. İsteğe bağlı olarak "Test Araması Yap" ile manuel arama yapabilirsiniz

### Dashboard

- **Dashboard**: Son arama sonuçları ve en çok görünen linkler
- **Raporlar**: Günlük, haftalık ve aylık detaylı raporlar
- **Ayarlar**: Arama parametrelerini düzenleme

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/settings` - Mevcut ayarları getir
- `PUT /api/settings` - Ayarları güncelle
- `POST /api/search/run` - Manuel arama yap
- `GET /api/search/results` - Arama sonuçlarını listele
- `GET /api/search/links/stats` - Link istatistikleri
- `GET /api/search/reports/daily` - Günlük raporlar
- `GET /api/search/reports/weekly` - Haftalık raporlar
- `GET /api/search/reports/monthly` - Aylık raporlar

## 🔧 Yapılandırma

### Environment Variables

- `SERPAPI_KEY`: SerpApi API anahtarı (varsayılan: kod içinde tanımlı)
- `DATABASE_URL`: Veritabanı URL'i (varsayılan: SQLite)
- `EMAIL_ENABLED`: Email bildirimleri (true/false, varsayılan: false)
- `SMTP_HOST`: SMTP sunucu (varsayılan: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (varsayılan: 587)
- `SMTP_USER`: SMTP kullanıcı adı
- `SMTP_PASSWORD`: SMTP şifresi
- `SMTP_FROM`: Gönderen email adresi
- `NOTIFICATION_EMAILS`: Bildirim gönderilecek email'ler (virgülle ayrılmış)

Email kurulumu için `EMAIL_SETUP.md` dosyasına bakın.

### Arama Konumları

- `Fatih,Istanbul`: Fatih, Istanbul
- `Istanbul`: Tüm İstanbul geneli

## 📊 Veritabanı

Varsayılan olarak SQLite kullanılır. Production için PostgreSQL önerilir:

```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🛠️ Geliştirme

### Backend Yapısı

```
backend/
├── app/
│   ├── main.py          # FastAPI uygulaması
│   ├── database.py       # Veritabanı modelleri
│   ├── serpapi_client.py # SerpApi entegrasyonu
│   ├── scheduler.py      # Zamanlanmış görevler
│   └── api/             # API endpoints
```

### Frontend Yapısı

```
frontend/
├── src/
│   ├── App.jsx          # Ana uygulama
│   └── components/      # React bileşenleri
```

## 📝 Notlar

- Bot varsayılan olarak 12 saatte bir arama yapar
- İlk sayfadaki tüm linkler (10 sonuç) kaydedilir
- Veritabanı otomatik olarak oluşturulur
- Scheduler uygulama başlatıldığında otomatik çalışır

## 🐛 Sorun Giderme

- **Arama çalışmıyor**: SerpApi API anahtarınızı kontrol edin
- **Veritabanı hatası**: Veritabanı dosyasına yazma izni olduğundan emin olun
- **Scheduler çalışmıyor**: Uygulama loglarını kontrol edin

## 📄 Lisans

Bu proje özel kullanım içindir.

