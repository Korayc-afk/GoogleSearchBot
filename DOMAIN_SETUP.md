# 🌐 Domain Bağlama Rehberi (Coolify)

## Coolify'da Domain Nasıl Bağlanır?

### Adım 1: Domain'i Coolify'a Ekleme

1. **Coolify Dashboard**'a gidin
2. Sol menüden **"Domains"** veya **"Domain Management"** sekmesine tıklayın
3. **"Add Domain"** veya **"+"** butonuna tıklayın
4. Domain adınızı girin (örn: `searchbot.com` veya `panel.searchbot.com`)
5. **"Save"** butonuna tıklayın

### Adım 2: DNS Ayarları

Domain'inizi Coolify'a bağlamak için DNS kayıtlarınızı güncellemeniz gerekiyor:

#### Seçenek 1: A Record (Önerilen)

Domain'inizin DNS ayarlarına gidin ve şu kaydı ekleyin:

```
Type: A
Name: @ (veya boş, root domain için)
Value: [Coolify sunucunuzun IP adresi]
TTL: 3600 (veya otomatik)
```

**Örnek:**
```
Type: A
Name: @
Value: 176.123.5.52
TTL: 3600
```

#### Seçenek 2: CNAME Record (Subdomain için)

Eğer subdomain kullanacaksanız (örn: `panel.searchbot.com`):

```
Type: CNAME
Name: panel (veya istediğiniz subdomain)
Value: [Coolify sunucunuzun hostname'i] (örn: coolify.example.com)
TTL: 3600
```

### Adım 3: Uygulamaya Domain Bağlama

1. Coolify Dashboard'da **uygulamanızı** seçin
2. **"Configuration"** veya **"Settings"** sekmesine gidin
3. **"Domains"** veya **"Custom Domain"** bölümünü bulun
4. **"Add Domain"** veya **"+"** butonuna tıklayın
5. Eklediğiniz domain'i seçin veya yeni domain girin
6. **"Save"** butonuna tıklayın

### Adım 4: SSL Sertifikası (HTTPS)

Coolify otomatik olarak Let's Encrypt ile SSL sertifikası oluşturur:

1. Domain eklendikten sonra **"SSL"** veya **"Certificates"** sekmesine gidin
2. **"Generate Certificate"** veya **"Enable SSL"** butonuna tıklayın
3. Let's Encrypt otomatik olarak sertifika oluşturacak (birkaç dakika sürebilir)

**Not:** SSL sertifikası için DNS kayıtlarının doğru yapılandırılmış olması gerekir.

### Adım 5: Multi-Site Domain Yapılandırması

Her site için farklı subdomain kullanabilirsiniz:

#### Örnek Yapılandırma:

```
Ana Domain: searchbot.com
├── default.searchbot.com → /default
├── gala.searchbot.com → /gala
├── hit.searchbot.com → /hit
├── office.searchbot.com → /office
└── pipo.searchbot.com → /pipo
```

#### Her Site İçin Domain Ekleme:

1. Coolify'da **aynı uygulamaya** birden fazla domain ekleyebilirsiniz
2. Her domain için:
   - **"Add Domain"** butonuna tıklayın
   - Domain adını girin (örn: `gala.searchbot.com`)
   - **"Save"** butonuna tıklayın
3. DNS'te her subdomain için CNAME kaydı ekleyin:
   ```
   Type: CNAME
   Name: gala
   Value: [Coolify hostname]
   ```

### Adım 6: Nginx Reverse Proxy Ayarları (Gerekirse)

Coolify genellikle otomatik olarak Nginx yapılandırması yapar, ancak özel ayarlar için:

1. Coolify Dashboard'da uygulamanızı seçin
2. **"Configuration"** > **"Nginx"** sekmesine gidin
3. Özel Nginx ayarları ekleyebilirsiniz

**Örnek Nginx Config (Multi-site için):**
```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Adım 7: Test Etme

1. DNS kayıtlarının yayılmasını bekleyin (5-60 dakika)
2. Domain'inizi tarayıcıda açın (örn: `https://gala.searchbot.com`)
3. Site'nin açıldığını kontrol edin
4. SSL sertifikasının çalıştığını kontrol edin (kilit ikonu)

## 🔍 DNS Kontrolü

DNS kayıtlarının doğru yapılandırıldığını kontrol etmek için:

### Windows:
```cmd
nslookup gala.searchbot.com
```

### Linux/Mac:
```bash
dig gala.searchbot.com
# veya
nslookup gala.searchbot.com
```

### Online DNS Checker:
- https://dnschecker.org/
- https://www.whatsmydns.net/

## 🐛 Sorun Giderme

### Domain çalışmıyor?
1. ✅ DNS kayıtlarının doğru olduğunu kontrol edin
2. ✅ DNS propagation'ın tamamlandığını bekleyin (24 saat sürebilir)
3. ✅ Coolify'da domain'in doğru eklendiğini kontrol edin
4. ✅ SSL sertifikasının oluşturulduğunu kontrol edin

### SSL sertifikası oluşturulamıyor?
1. ✅ DNS kayıtlarının doğru olduğunu kontrol edin
2. ✅ Port 80 ve 443'ün açık olduğunu kontrol edin
3. ✅ Let's Encrypt rate limit'ini kontrol edin
4. ✅ Domain'in başka bir yerde kullanılmadığını kontrol edin

### Subdomain'ler çalışmıyor?
1. ✅ Her subdomain için ayrı DNS kaydı eklediğinizden emin olun
2. ✅ Coolify'da her subdomain'i ayrı ayrı eklediğinizden emin olun
3. ✅ Nginx yapılandırmasını kontrol edin

## 📝 Örnek DNS Kayıtları

### Namecheap için:
```
Type: A Record
Host: @
Value: 176.123.5.52
TTL: Automatic

Type: CNAME Record
Host: gala
Value: your-coolify-host.com
TTL: Automatic
```

### GoDaddy için:
```
Type: A
Name: @
Value: 176.123.5.52
TTL: 600 seconds

Type: CNAME
Name: gala
Value: your-coolify-host.com
TTL: 600 seconds
```

### Cloudflare için:
1. DNS sekmesine gidin
2. **"Add record"** butonuna tıklayın
3. Type: **A** veya **CNAME** seçin
4. Name ve Value'yu girin
5. Proxy durumunu ayarlayın (genellikle "DNS only" önerilir)

## ✅ Kontrol Listesi

- [ ] Domain Coolify'a eklendi
- [ ] DNS kayıtları yapılandırıldı
- [ ] DNS propagation tamamlandı (test edildi)
- [ ] Domain uygulamaya bağlandı
- [ ] SSL sertifikası oluşturuldu
- [ ] HTTPS çalışıyor
- [ ] Tüm subdomain'ler çalışıyor
- [ ] Multi-site routing çalışıyor (/gala, /hit, vb.)

## 🎉 Başarılı!

Artık domain'iniz bağlandı ve siteleriniz şu şekilde erişilebilir:
- `https://searchbot.com/default` (veya sadece `https://searchbot.com`)
- `https://gala.searchbot.com` → `/gala`
- `https://hit.searchbot.com` → `/hit`
- vb.

