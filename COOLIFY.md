# Coolify Deployment Guide

Bu projeyi Coolify'da deploy etmek için aşağıdaki adımları izleyin:

## 1. Repository Hazırlığı

Projeyi Git repository'nize push edin.

## 2. Coolify'da Uygulama Oluşturma

1. Coolify dashboard'una gidin
2. "New Resource" > "Application" seçin
3. Git repository'nizi bağlayın

## 3. Build Ayarları

- **Build Pack**: `Dockerfile` (backend/Dockerfile kullanılacak)
- **Dockerfile Path**: `backend/Dockerfile`
- **Build Context**: `backend/`

## 4. Environment Variables

Aşağıdaki environment variable'ları ekleyin:

```
SERPAPI_KEY=bb970a4dea7a4ea4952712cd9bd6d6cb73765f27eee2bcb221bc63c7ba7b6068
DATABASE_URL=sqlite:///./data/searchbot.db
PORT=8000
```

## 5. Volume Ayarları

Veritabanı ve loglar için bir volume oluşturun:

- **Path**: `/app/data`
- **Mount Point**: `./data` (host'ta)

## 6. Port Ayarları

- **Port**: `8000`
- **Public Port**: İstediğiniz port (örn: 80, 443)

## 7. Health Check

Health check endpoint'i otomatik olarak çalışacak:
- **Path**: `/api/health`

## 8. Deploy

"Deploy" butonuna tıklayın ve uygulamanın başlamasını bekleyin.

## 9. İlk Kurulum

1. Uygulama URL'ine gidin
2. Ayarlar sayfasından arama parametrelerini yapılandırın
3. Test araması yaparak sistemin çalıştığını doğrulayın

## Notlar

- Uygulama başladığında scheduler otomatik olarak çalışmaya başlar
- Veritabanı otomatik olarak oluşturulur
- Logları Coolify dashboard'undan takip edebilirsiniz
- Production için PostgreSQL kullanmanız önerilir (DATABASE_URL değiştirin)

## PostgreSQL Kullanımı (Opsiyonel)

PostgreSQL kullanmak isterseniz:

1. Coolify'da bir PostgreSQL servisi oluşturun
2. Environment variable'ı güncelleyin:
   ```
   DATABASE_URL=postgresql://user:password@postgres-service:5432/dbname
   ```
3. `requirements.txt`'e `psycopg2-binary` ekleyin (veya Dockerfile'da)

