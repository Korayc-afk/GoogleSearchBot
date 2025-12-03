# 💾 Verilerin Kalıcı Olması - Persistent Storage Rehberi

## ⚠️ ÖNEMLİ: Her Deploy'da Verilerin Korunması

Bu rehber, her deploy/güncelleme sonrasında verilerinizin kaybolmaması için gerekli ayarları açıklar.

## 🎯 Sorun

Varsayılan olarak Docker container'ları **ephemeral** (geçici) çalışır. Yani:
- Container silinirse → Veriler kaybolur ❌
- Container yeniden başlatılırsa → Veriler kaybolur ❌
- Yeni deploy yapılırsa → Veriler kaybolur ❌

## ✅ Çözüm: Persistent Storage (Kalıcı Depolama)

Verilerinizi container dışında, **host sisteminde** saklamak için **Volume Mount** kullanmalısınız.

## 📍 Veriler Nerede Saklanıyor?

**Production (Coolify/Docker):**
- Veritabanı path: `/data/{site_id}/searchbot.db`
- Örnek: `/data/default/searchbot.db` → Padisah
- Örnek: `/data/gala/searchbot.db` → Gala

**Development (Local):**
- Veritabanı path: `./data/{site_id}/searchbot.db`

## 🔧 Coolify'da Persistent Storage Ayarlama

### Adım 1: Coolify Dashboard'a Gidin

1. Coolify'ı açın
2. Uygulamanızı seçin
3. **"Configuration"** veya **"Settings"** sekmesine gidin

### Adım 2: Persistent Storage Ekleme

1. **"Persistent Storage"** veya **"Volumes"** bölümünü bulun
2. **"Add Volume"** veya **"+"** butonuna tıklayın
3. Şu ayarları yapın:

```
Name: searchbot-data (veya istediğiniz bir isim)
Source Path: /data
Destination Path: /data
Size: 1GB (veya daha fazla - opsiyonel)
```

**ÖNEMLİ NOTLAR:**
- ✅ **Source Path** ve **Destination Path** aynı olmalı: `/data`
- ✅ Container içindeki path'i yazın (host path değil)
- ✅ Coolify otomatik olarak host'ta bir volume oluşturur
- ✅ Bu volume container silinse bile kalır

### Adım 3: Environment Variable (Opsiyonel ama Önerilen)

**"Environment Variables"** bölümüne gidin ve ekleyin:

```
DATA_DIR=/data
```

Bu, uygulamanın veritabanı path'ini bilmesini sağlar.

### Adım 4: Container'ı Yeniden Başlatın

1. Volume'u ekledikten sonra
2. **"Restart"** veya **"Redeploy"** butonuna tıklayın
3. Container yeniden başlatılacak ve volume mount edilecek

## ✅ Doğrulama

### Verilerin Korunduğunu Kontrol Edin:

1. **İlk Deploy:**
   - Ayarları yapın
   - Test araması yapın
   - Verilerin kaydedildiğini kontrol edin

2. **Yeni Deploy:**
   - Kod değişikliği yapın
   - GitHub'a push edin
   - Coolify otomatik deploy yapsın
   - **Verilerin hala orada olduğunu kontrol edin** ✅

### Volume'un Mount Edildiğini Kontrol Edin:

Coolify'da container loglarına bakın veya container'a bağlanın:

```bash
# Container içinde /data klasörünün var olduğunu kontrol edin
ls -la /data

# Veritabanı dosyalarının var olduğunu kontrol edin
ls -la /data/default/
ls -la /data/gala/
```

## 🚨 Sorun Giderme

### Sorun 1: Deploy Sonrası Veriler Kayboldu

**Çözüm:**
1. Persistent Storage'ın doğru ayarlandığını kontrol edin
2. Volume'un mount edildiğini kontrol edin
3. Environment variable `DATA_DIR=/data` ekleyin
4. Container'ı yeniden başlatın

### Sorun 2: Volume Mount Edilmedi

**Çözüm:**
1. Coolify'da volume ayarlarını kontrol edin
2. Source ve Destination path'lerin `/data` olduğundan emin olun
3. Container'ı yeniden başlatın

### Sorun 3: Permission Hatası

**Çözüm:**
1. Container'ın `/data` klasörüne yazma izni olduğundan emin olun
2. Coolify genellikle bunu otomatik halleder
3. Gerekirse volume'u silip yeniden oluşturun

## 📊 Veri Yedekleme

### Otomatik Yedekleme (Önerilen)

Coolify'ın backup özelliğini kullanın:
1. Coolify Dashboard → Uygulama → **"Backups"**
2. Düzenli backup zamanlaması ayarlayın
3. Backup'ları düzenli olarak kontrol edin

### Manuel Yedekleme

```bash
# Container'dan veritabanını kopyalayın
docker cp <container_id>:/data/default/searchbot.db ./backup_searchbot.db

# Tüm site'ları yedekleyin
docker cp <container_id>:/data ./backup_data
```

## 🔄 Deploy Sonrası Kontrol Listesi

Her deploy sonrası şunları kontrol edin:

- [ ] Volume mount edilmiş mi? (`/data` klasörü var mı?)
- [ ] Veritabanı dosyaları var mı? (`/data/{site_id}/searchbot.db`)
- [ ] Ayarlar korunmuş mu? (Settings sayfasında kontrol edin)
- [ ] Son arama sonuçları görünüyor mu? (Dashboard'da kontrol edin)
- [ ] Yeni arama yapılabiliyor mu? (Test araması yapın)

## 📝 Özet

**Verilerinizin kalıcı olması için:**

1. ✅ **Persistent Storage** ekleyin: `/data` → `/data`
2. ✅ **Environment Variable** ekleyin: `DATA_DIR=/data`
3. ✅ **Container'ı yeniden başlatın**
4. ✅ **Doğrulama yapın**: Verilerin korunduğunu kontrol edin

**Artık her deploy sonrası verileriniz korunacak!** 🎉

## 🆘 Yardım

Sorun yaşıyorsanız:
1. Coolify loglarını kontrol edin
2. Container'a bağlanıp `/data` klasörünü kontrol edin
3. Volume mount ayarlarını tekrar gözden geçirin
4. Environment variable'ları kontrol edin

