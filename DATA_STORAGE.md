# 💾 Veri Saklama ve Raporlama

## 📍 Veriler Nerede Saklanıyor?

Botunuzun tüm verileri **SQLite veritabanı** dosyasında saklanıyor:

- **Dosya Konumu**: `/app/data/searchbot.db`
- **Veritabanı Türü**: SQLite (hafif, dosya tabanlı)
- **İçerik**:
  - Arama ayarları (kelime, konum, interval)
  - Tüm arama sonuçları (tarih, saat)
  - Her aramadaki linkler (URL, başlık, pozisyon, domain)
  - Link istatistikleri (görünme sayısı, pozisyon değişiklikleri)

## 🗄️ Veritabanı Yapısı

### 1. `search_settings` Tablosu
Arama ayarlarını saklar:
- `search_query`: Aranacak kelime(ler) (virgülle ayrılmış)
- `location`: Arama konumu (örn: "Fatih,Istanbul")
- `enabled`: Bot aktif mi?
- `interval_hours`: Arama sıklığı (artık kullanılmıyor - her saat başı çalışıyor)

### 2. `search_results` Tablosu
Her aramayı kaydeder:
- `search_date`: Arama tarihi ve saati
- `total_results`: Toplam sonuç sayısı
- `settings_id`: Hangi ayarlarla yapıldı

### 3. `search_links` Tablosu
Her aramadaki linkleri saklar:
- `url`: Link URL'i
- `title`: Başlık
- `snippet`: Açıklama
- `position`: Pozisyon (1-10, ilk sayfa)
- `domain`: Domain adı
- `created_at`: Kayıt tarihi

## 🔒 Verilerin Kalıcı Olması İçin (Coolify)

**ÖNEMLİ:** Docker container silinirse veriler kaybolur! Verilerin kalıcı olması için **Persistent Storage** ayarlamanız gerekiyor.

### Coolify'da Persistent Storage Ayarlama:

1. **Coolify Dashboard**'a gidin
2. Uygulamanızı seçin
3. **"Configuration"** veya **"Settings"** sekmesine gidin
4. **"Persistent Storage"** veya **"Volumes"** bölümünü bulun
5. **"Add Volume"** veya **"+"** butonuna tıklayın
6. **"Add Volume Mount"** dialog'unda şu ayarları yapın:
   - **Name**: `searchbot-data` (veya istediğiniz bir isim)
   - **Source Path**: `/app/data` (container içindeki path)
   - **Destination Path**: `/app/data` ⚠️ **BU ALAN ÖNEMLİ!** Container içindeki path'i yazın
   - **Size**: (Opsiyonel - Bazı Coolify versiyonlarında otomatik ayarlanır veya görünmeyebilir. Eğer görünüyorsa en az 1GB ayarlayın)

### Volume Ayarları Detayı:

```
Name: searchbot-data
Source Path: /app/data
Destination Path: /app/data  ← BU ALAN ÖNEMLİ!
```

**Not:** Volume'u ekledikten sonra container'ı yeniden başlatmanız gerekebilir.

## 📊 Raporlama ve Veri Erişimi

### Dashboard Üzerinden:
- **Dashboard**: Genel istatistikler
- **Reports**: Günlük, haftalık, aylık raporlar
- **Charts**: Grafikler ve görselleştirmeler
- **Analytics**: Gelişmiş filtreleme ve analiz

### Excel Export:
- **Daily Report**: Günlük arama sonuçları
- **Summary Report**: Link istatistikleri
- **Position History**: Belirli bir URL'in pozisyon geçmişi

### API Endpoints:
- `/api/search/results` - Arama sonuçları
- `/api/search/links/stats` - Link istatistikleri
- `/api/export/daily-excel` - Excel export
- `/api/analytics/*` - Analitik veriler

## 🔄 Veri Yedekleme

### Manuel Yedekleme:
1. Coolify'da container'a bağlanın
2. Veritabanı dosyasını kopyalayın:
   ```bash
   docker cp <container_id>:/app/data/searchbot.db ./backup_searchbot.db
   ```

### Otomatik Yedekleme (Önerilen):
- Coolify'ın backup özelliğini kullanın
- Veya cron job ile düzenli yedekleme yapın

## 📈 Veri Büyüklüğü

- **Her arama**: ~10 link (ilk sayfa)
- **Her link**: ~500 byte veri
- **Günlük veri**: ~5KB (24 arama)
- **Aylık veri**: ~150KB
- **Yıllık veri**: ~1.8MB

**Sonuç:** Veritabanı çok küçük kalır, 1GB volume yeterli.

## 🚨 Veri Kaybını Önleme

1. ✅ **Persistent Storage** mutlaka ayarlayın
2. ✅ Düzenli **yedekleme** yapın
3. ✅ Container'ı silmeden önce **volume'u kontrol edin**
4. ✅ Production'da **PostgreSQL** kullanmayı düşünün (daha güvenli)

## 🔧 PostgreSQL'e Geçiş (Opsiyonel)

Daha büyük projeler için PostgreSQL önerilir:

1. Coolify'da PostgreSQL servisi oluşturun
2. Environment variable'ı güncelleyin:
   ```
   DATABASE_URL=postgresql://user:password@postgres-service:5432/searchbot
   ```
3. `requirements.txt`'e ekleyin:
   ```
   psycopg2-binary
   ```

## 📝 Veri Temizleme

Eski verileri silmek için:
- Dashboard'dan manuel silme
- API endpoint'leri ile programatik silme
- SQL sorguları ile direkt veritabanından silme

**Not:** Veri silme işlemleri geri alınamaz, dikkatli olun!

