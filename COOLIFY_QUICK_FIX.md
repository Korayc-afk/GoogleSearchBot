# 🔧 Coolify Persistent Storage Hızlı Düzeltme

## ⚠️ Sorun

Mevcut Persistent Storage ayarınız `/app/data` kullanıyor, ancak yeni kod `/data` kullanıyor. Bu yüzden veriler kayboluyor.

## ✅ Çözüm (3 Adım)

### Adım 1: Persistent Storage Path'ini Güncelle

1. Coolify Dashboard → GoogleSearchBot → **Configuration** → **Persistent Storage**
2. Mevcut volume'u bulun (şu anda `/app/data` olan)
3. **"Update"** butonuna tıklayın
4. Path'leri şu şekilde güncelleyin:

```
Volume Name: e88oocg4wogwskgc8wg04os4-searchbot-data (değiştirmeyin)
Source Path: /data        ← BUNU DEĞİŞTİRİN
Destination Path: /data   ← BUNU DEĞİŞTİRİN
```

5. **"Update"** butonuna tıklayın

### Adım 2: Environment Variable Ekle

1. **Configuration** → **Environment Variables** sekmesine gidin
2. **"+ Add"** butonuna tıklayın
3. Şu değerleri ekleyin:

```
Key: DATA_DIR
Value: /data
```

4. **"Save"** veya **"Add"** butonuna tıklayın

### Adım 3: Container'ı Yeniden Başlat

1. Üst kısımdaki **"Restart"** butonuna tıklayın
2. Veya **"Redeploy"** butonuna tıklayın (daha güvenli)

## ✅ Doğrulama

Deploy sonrası kontrol edin:

1. **Terminal** sekmesine gidin
2. Şu komutu çalıştırın:
   ```bash
   ls -la /data
   ```
3. Şunları görmelisiniz:
   ```
   default/
   gala/
   hit/
   office/
   pipo/
   ```
4. Her klasörde `searchbot.db` dosyası olmalı

## 🚨 Eski Verileri Taşıma (Opsiyonel)

Eğer `/app/data` altında eski verileriniz varsa, onları taşıyabilirsiniz:

1. **Terminal** sekmesine gidin
2. Şu komutları çalıştırın:
   ```bash
   # Eski verileri kontrol et
   ls -la /app/data
   
   # Eğer veri varsa, yeni yere taşı
   cp -r /app/data/* /data/ 2>/dev/null || echo "Eski veri yok veya zaten taşındı"
   ```

## 📝 Özet

**Yapılacaklar:**
1. ✅ Source Path: `/app/data` → `/data`
2. ✅ Destination Path: `/app/data` → `/data`
3. ✅ Environment Variable: `DATA_DIR=/data` ekle
4. ✅ Container'ı yeniden başlat

**Artık verileriniz korunacak!** 🎉

