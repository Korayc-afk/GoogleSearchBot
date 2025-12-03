"""
Eski veritabanını yeni multi-site yapıya taşıma script'i
Eski: data/searchbot.db
Yeni: data/default/searchbot.db
"""
import os
import shutil
import sqlite3
from pathlib import Path

def migrate_old_database():
    """Eski veritabanını yeni yapıya taşır"""
    # Path'leri belirle
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    old_db_path = data_dir / "searchbot.db"
    new_site_dir = data_dir / "default"
    new_db_path = new_site_dir / "searchbot.db"
    
    print("=" * 60)
    print("🔄 Veritabanı Migration Başlatılıyor...")
    print("=" * 60)
    
    # Eski veritabanı var mı kontrol et
    if not old_db_path.exists():
        print(f"❌ Eski veritabanı bulunamadı: {old_db_path}")
        print("✅ Yeni yapı zaten kullanılıyor olabilir.")
        return
    
    print(f"✅ Eski veritabanı bulundu: {old_db_path}")
    
    # Yeni site dizinini oluştur
    new_site_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Yeni site dizini oluşturuldu: {new_site_dir}")
    
    # Eğer yeni veritabanı zaten varsa, yedekle
    if new_db_path.exists():
        backup_path = new_site_dir / "searchbot.db.backup"
        print(f"⚠️  Yeni veritabanı zaten var, yedekleniyor: {backup_path}")
        shutil.copy2(new_db_path, backup_path)
    
    # Eski veritabanını yeni konuma kopyala
    print(f"📋 Veritabanı kopyalanıyor: {old_db_path} -> {new_db_path}")
    shutil.copy2(old_db_path, new_db_path)
    print(f"✅ Veritabanı kopyalandı!")
    
    # Veritabanını kontrol et
    try:
        conn = sqlite3.connect(new_db_path)
        cursor = conn.cursor()
        
        # Tabloları kontrol et
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📊 Veritabanı tabloları:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} kayıt")
        
        conn.close()
        print("\n✅ Veritabanı kontrol edildi, tüm veriler mevcut!")
        
        # Eski veritabanını yedekle (silmeden önce)
        old_backup = data_dir / "searchbot.db.old_backup"
        if not old_backup.exists():
            print(f"\n💾 Eski veritabanı yedekleniyor: {old_backup}")
            shutil.copy2(old_db_path, old_backup)
            print(f"✅ Yedek oluşturuldu: {old_backup}")
        
        print("\n" + "=" * 60)
        print("✅ Migration tamamlandı!")
        print("=" * 60)
        print(f"\n📍 Yeni veritabanı konumu: {new_db_path}")
        print(f"📍 Eski veritabanı yedeği: {old_backup}")
        print(f"\n💡 Artık '/default' veya '/' URL'inden eski verilerinize erişebilirsiniz!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        raise

if __name__ == "__main__":
    migrate_old_database()

