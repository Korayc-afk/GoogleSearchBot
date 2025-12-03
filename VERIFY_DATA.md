# ✅ Veri Doğrulama Komutları

## 📋 Kontrol Listesi

Terminal'de şu komutları çalıştırarak verilerinizin durumunu kontrol edebilirsiniz:

### 1. Tüm Site Klasörlerini Listele
```bash
ls -la /data
```

**Beklenen Çıktı:**
- `default/` - Padisah site
- `padisah/` - Padisah site (alternatif)
- `gala/` - Gala site (henüz oluşmamış olabilir)
- `hit/` - Hit site (henüz oluşmamış olabilir)
- `office/` - Office site (henüz oluşmamış olabilir)
- `pipo/` - Pipo site (henüz oluşmamış olabilir)

### 2. Default Site Veritabanını Kontrol Et
```bash
ls -la /data/default/
```

**Beklenen Çıktı:**
```
searchbot.db
```

### 3. Padisah Site Veritabanını Kontrol Et
```bash
ls -la /data/padisah/
```

**Beklenen Çıktı:**
```
searchbot.db
```

### 4. Veritabanı Dosya Boyutunu Kontrol Et
```bash
du -sh /data/default/searchbot.db
du -sh /data/padisah/searchbot.db
```

**Beklenen Çıktı:**
- Eğer veri varsa: `8.0K` veya daha büyük
- Eğer veri yoksa: Dosya bulunamaz veya çok küçük

### 5. Tüm Site'ların Veritabanı Durumunu Kontrol Et
```bash
find /data -name "searchbot.db" -exec ls -lh {} \;
```

**Beklenen Çıktı:**
Her site için veritabanı dosyası listelenir.

## 🔍 Sorun Giderme

### Sorun: Veritabanı Dosyası Yok

**Çözüm:**
1. Dashboard'a gidin
2. Settings sayfasına gidin
3. "Test Araması Yap" butonuna tıklayın
4. Arama tamamlandıktan sonra tekrar kontrol edin:
   ```bash
   ls -la /data/default/
   ```

### Sorun: Klasör Yok

**Çözüm:**
1. İlgili site'ye gidin (örn: `/gala`)
2. Settings'ten test araması yapın
3. Klasör otomatik oluşacak

### Sorun: Veriler Görünmüyor

**Çözüm:**
1. Container'ı yeniden başlatın
2. Environment variable'ı kontrol edin: `DATA_DIR=/data`
3. Persistent storage mount'unu kontrol edin

## ✅ Başarı Kriterleri

- [ ] `/data` klasörü var
- [ ] Site klasörleri var (`default`, `padisah`, vb.)
- [ ] Her site klasöründe `searchbot.db` dosyası var
- [ ] Veritabanı dosyaları 0'dan büyük (veri içeriyor)
- [ ] Dashboard'da arama sonuçları görünüyor

## 📊 Veri Durumu Kontrolü

Eğer veritabanı dosyaları varsa ama Dashboard'da görünmüyorsa:

1. **API'yi kontrol edin:**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Veritabanı içeriğini kontrol edin (SQLite):**
   ```bash
   sqlite3 /data/default/searchbot.db "SELECT COUNT(*) FROM search_results;"
   ```

3. **Logları kontrol edin:**
   - Coolify → Logs sekmesi
   - Hata mesajlarını kontrol edin

## 🎯 Sonuç
 
Eğer tüm kontroller başarılıysa, verileriniz kalıcı olarak saklanıyor demektir! 🎉  

   