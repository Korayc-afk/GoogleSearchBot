import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime

# Email ayarları (environment variables'dan alınacak)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
NOTIFICATION_EMAILS = os.getenv("NOTIFICATION_EMAILS", "").split(",") if os.getenv("NOTIFICATION_EMAILS") else []


class EmailService:
    def __init__(self):
        self.enabled = EMAIL_ENABLED and SMTP_USER and SMTP_PASSWORD
        self.recipients = [email.strip() for email in NOTIFICATION_EMAILS if email.strip()]
    
    async def send_email(
        self,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """Email gönder"""
        if not self.enabled:
            print(f"Email gönderilemedi (devre dışı): {subject}")
            return False
        
        if not recipients:
            recipients = self.recipients
        
        if not recipients:
            print("Email alıcısı belirtilmedi")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = SMTP_FROM
            message["To"] = ", ".join(recipients)
            
            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                use_tls=True
            )
            
            print(f"Email gönderildi: {subject} -> {recipients}")
            return True
        except Exception as e:
            print(f"Email gönderme hatası: {str(e)}")
            return False
    
    async def send_position_change_alert(
        self,
        url: str,
        domain: str,
        old_position: int,
        new_position: int,
        change: int
    ):
        """Pozisyon değişikliği bildirimi"""
        direction = "yükseldi" if change < 0 else "düştü"
        emoji = "📈" if change < 0 else "📉"
        
        subject = f"{emoji} Pozisyon Değişikliği: {domain}"
        
        body = f"""
        <html>
        <body>
            <h2>Pozisyon Değişikliği Bildirimi</h2>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>URL:</strong> {url}</p>
            <p><strong>Eski Pozisyon:</strong> #{old_position}</p>
            <p><strong>Yeni Pozisyon:</strong> #{new_position}</p>
            <p><strong>Değişim:</strong> {abs(change)} pozisyon {direction}</p>
            <p><strong>Tarih:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, body, html=True)
    
    async def send_daily_summary(
        self,
        total_searches: int,
        unique_links: int,
        top_links: List[Dict],
        date: str
    ):
        """Günlük özet email"""
        subject = f"📊 Google Search Bot - Günlük Özet ({date})"
        
        top_links_html = ""
        for i, link in enumerate(top_links[:10], 1):
            top_links_html += f"""
            <tr>
                <td>{i}</td>
                <td>{link.get('domain', 'N/A')}</td>
                <td>#{link.get('average_position', 0).toFixed(1)}</td>
                <td>{link.get('total_appearances', 0)}</td>
            </tr>
            """
        
        body = f"""
        <html>
        <body>
            <h2>Günlük Arama Özeti - {date}</h2>
            <div style="margin: 20px 0;">
                <p><strong>Toplam Arama:</strong> {total_searches}</p>
                <p><strong>Benzersiz Link:</strong> {unique_links}</p>
            </div>
            <h3>En Çok Görünen Linkler</h3>
            <table border="1" cellpadding="10" style="border-collapse: collapse;">
                <tr>
                    <th>Sıra</th>
                    <th>Domain</th>
                    <th>Ort. Pozisyon</th>
                    <th>Görünme</th>
                </tr>
                {top_links_html}
            </table>
        </body>
        </html>
        """
        
        return await self.send_email(subject, body, html=True)
    
    async def send_critical_drop_alert(
        self,
        url: str,
        domain: str,
        old_position: int,
        new_position: int
    ):
        """Kritik düşüş uyarısı (5+ pozisyon düşüşü)"""
        drop = new_position - old_position
        
        subject = f"⚠️ KRİTİK: {domain} - {drop} Pozisyon Düştü!"
        
        body = f"""
        <html>
        <body>
            <h2 style="color: red;">Kritik Pozisyon Düşüşü!</h2>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>URL:</strong> {url}</p>
            <p><strong>Eski Pozisyon:</strong> #{old_position}</p>
            <p><strong>Yeni Pozisyon:</strong> #{new_position}</p>
            <p><strong>Düşüş:</strong> {drop} pozisyon</p>
            <p><strong>Tarih:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="color: red; font-weight: bold;">Lütfen bu durumu inceleyin!</p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, body, html=True)


# Global email service instance
email_service = EmailService()


