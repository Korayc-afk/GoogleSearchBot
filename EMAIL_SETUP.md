# 📧 Email Bildirimleri Kurulumu

Bot, pozisyon değişikliklerinde ve günlük özetlerde email gönderebilir.

## Environment Variables

Coolify'da aşağıdaki environment variable'ları ekleyin:

```
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
NOTIFICATION_EMAILS=recipient1@example.com,recipient2@example.com
```

## Gmail Kullanımı

1. Google Account'unuza gidin
2. **Security** > **2-Step Verification** (etkinleştirin)
3. **App Passwords** oluşturun
4. Oluşturulan app password'ü `SMTP_PASSWORD` olarak kullanın

## Email Bildirimleri

### Otomatik Bildirimler

1. **Pozisyon Değişiklikleri**: 3+ pozisyon değişikliğinde email gönderilir
2. **Kritik Düşüşler**: 5+ pozisyon düşüşünde özel uyarı email'i
3. **Günlük Özet**: Her gün saat 09:00'da günlük özet email'i

### Email İçeriği

- Pozisyon değişiklikleri: Domain, URL, eski/yeni pozisyon, değişim miktarı
- Günlük özet: Toplam arama, benzersiz link sayısı, en çok görünen linkler

## Test

Email ayarlarını test etmek için:
1. Ayarları kaydedin
2. Test araması yapın
3. Pozisyon değişikliği olursa email gelecektir

## Notlar

- Email gönderimi asenkron çalışır (bot performansını etkilemez)
- Email gönderilemezse loglarda hata görünecektir
- Production'da email gönderimi için güvenli SMTP kullanın



