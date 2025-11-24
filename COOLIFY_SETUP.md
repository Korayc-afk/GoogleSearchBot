# 🚀 Coolify Deployment - Detaylı Rehber

## Adım 1: GitHub Repository Hazır

✅ Repository: `https://github.com/Korayc-afk/GoogleSearchBot.git` (Private)

## Adım 2: Coolify'da Yeni Uygulama Oluştur

1. Coolify dashboard'una gidin
2. **"New Resource"** butonuna tıklayın
3. **"Applications"** > **"Git Based"** > **"Private Repository (with GitHub App)"** seçin
   - Eğer GitHub App yoksa, **"Private Repository (with Deploy Key)"** kullanabilirsiniz
4. Repository URL'ini girin: `https://github.com/Korayc-afk/GoogleSearchBot.git`
5. Branch: `main`
6. Build Pack: **"Dockerfile"** seçin
7. Dockerfile Path: `backend/Dockerfile`
8. Build Context: `backend/`

## Adım 3: Environment Variables Ekleme

### Environment Variables Nerede?

Coolify'da environment variable'ları eklemek için:

1. **Uygulama oluşturulduktan sonra:**
   - Uygulama detay sayfasına gidin
   - Sağ tarafta veya üst menüde **"Environment"** veya **"Variables"** sekmesine tıklayın
   - Ya da **"Settings"** > **"Environment Variables"** bölümüne gidin

2. **"Add Variable"** veya **"+"** butonuna tıklayın

3. Aşağıdaki variable'ları ekleyin:

| Key | Value |
|-----|-------|
| `SERPAPI_KEY` | `bb970a4dea7a4ea4952712cd9bd6d6cb73765f27eee2bcb221bc63c7ba7b6068` |
| `DATABASE_URL` | `sqlite:///./data/searchbot.db` |
| `PORT` | `8000` |

### Önemli Notlar:

- ✅ Her variable için **Key** ve **Value** alanlarını doldurun
- ✅ Variable'ları ekledikten sonra **"Save"** veya **"Deploy"** butonuna tıklayın
- ✅ Production ve Staging environment'ları için ayrı variable'lar tanımlayabilirsiniz

## Adım 4: Volume Ayarları (Veritabanı için)

Veritabanı dosyasının kalıcı olması için:

1. Uygulama ayarlarında **"Volumes"** veya **"Storage"** bölümüne gidin
2. Yeni volume ekleyin:
   - **Path**: `/app/data`
   - **Name**: `searchbot-data` (veya istediğiniz bir isim)

## Adım 5: Port Ayarları

1. Uygulama ayarlarında **"Ports"** bölümüne gidin
2. **Container Port**: `8000`
3. **Public Port**: İstediğiniz port (örn: 80, 443, 3000)

## Adım 6: Health Check

Coolify otomatik olarak health check yapacak:
- **Path**: `/api/health`
- **Interval**: 30 saniye

## Adım 7: Deploy

1. Tüm ayarları yaptıktan sonra **"Deploy"** butonuna tıklayın
2. Build işlemi başlayacak (birkaç dakika sürebilir)
3. Logları takip ederek build'in başarılı olduğundan emin olun

## Adım 8: İlk Kurulum

1. Uygulama URL'ine gidin (örn: `http://your-domain.com` veya `http://your-ip:port`)
2. Dashboard açılacak
3. **Ayarlar** sekmesine gidin
4. Arama parametrelerini yapılandırın:
   - **Aranacak Kelime**: `padişah bet` (veya istediğiniz)
   - **Konum**: `Fatih,Istanbul` veya `Istanbul`
   - **Interval**: `12` saat
5. **"Ayarları Kaydet"** butonuna tıklayın
6. **"Test Araması Yap"** ile sistemin çalıştığını doğrulayın

## 🔍 Environment Variables Ekran Görüntüsü Konumu

Coolify'da environment variable'lar genellikle şu yerlerde bulunur:

1. **Uygulama Detay Sayfası:**
   ```
   [Uygulama Adı] > [Environment/Variables] Tab
   ```

2. **Uygulama Ayarları:**
   ```
   [Uygulama Adı] > Settings > Environment Variables
   ```

3. **Deploy Sırasında:**
   - Deploy ayarlarında "Environment" bölümü

## 📝 Örnek Environment Variables Ekranı

```
┌─────────────────────────────────────┐
│ Environment Variables               │
├─────────────────────────────────────┤
│ Key              │ Value            │
├─────────────────────────────────────┤
│ SERPAPI_KEY      │ bb970a4...      │
│ DATABASE_URL     │ sqlite:///...   │
│ PORT             │ 8000             │
└─────────────────────────────────────┘
[+ Add Variable] [Save]
```

## 🐛 Sorun Giderme

### Environment Variable'lar görünmüyor?
- Uygulama ayarlarına gidin
- "Environment" veya "Variables" sekmesini kontrol edin
- Farklı environment'lar (production/staging) için ayrı variable'lar olabilir

### Variable'lar çalışmıyor?
- Variable'ları ekledikten sonra uygulamayı yeniden deploy edin
- Variable isimlerinin doğru olduğundan emin olun (büyük/küçük harf duyarlı)
- Logları kontrol edin

## ✅ Kontrol Listesi

- [ ] GitHub repository private olarak oluşturuldu
- [ ] Coolify'da uygulama oluşturuldu
- [ ] GitHub App veya Deploy Key bağlandı
- [ ] Dockerfile path doğru ayarlandı (`backend/Dockerfile`)
- [ ] Environment variables eklendi (SERPAPI_KEY, DATABASE_URL, PORT)
- [ ] Volume ayarlandı (`/app/data`)
- [ ] Port ayarlandı (8000)
- [ ] Deploy başarılı
- [ ] Health check çalışıyor
- [ ] Dashboard erişilebilir
- [ ] İlk arama yapıldı ve çalışıyor

## 🎉 Başarılı!

Artık botunuz 12 saatte bir otomatik olarak arama yapacak ve sonuçları kaydedecek!

