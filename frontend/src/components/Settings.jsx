import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { formatInTimeZone } from 'date-fns-tz'

function Settings({ API_BASE, settings, onUpdate, siteId = 'default' }) {
  const [formData, setFormData] = useState({
    search_query: '',
    location: 'Fatih,Istanbul',
    enabled: true,
    interval_hours: 12,
    serpapi_key: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [schedulerStatus, setSchedulerStatus] = useState(null)
  const [stats, setStats] = useState({
    totalSearches: 0,
    totalLinks: 0,
    uniqueDomains: 0
  })
  const [recentSearches, setRecentSearches] = useState([])
  const [loadingStats, setLoadingStats] = useState(true)

  useEffect(() => {
    if (settings) {
      setFormData({
        search_query: settings.search_query || '',
        location: settings.location || 'Fatih,Istanbul',
        enabled: settings.enabled !== undefined ? settings.enabled : true,
        interval_hours: settings.interval_hours || 12,
        serpapi_key: settings.serpapi_key || ''
      })
    }
    fetchStats()
    const interval = setInterval(fetchStats, 30000) // 30 saniyede bir güncelle
    return () => clearInterval(interval)
  }, [settings, siteId])

  const fetchStats = async () => {
    try {
      const [schedulerRes, resultsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/settings/scheduler-status?site_id=${siteId}`),
        axios.get(`${API_BASE}/search/results?limit=5&site_id=${siteId}`),
        axios.get(`${API_BASE}/search/stats?site_id=${siteId}`).catch(() => null)
      ])

      setSchedulerStatus(schedulerRes.data)
      setRecentSearches(resultsRes.data)
      
      // İstatistikleri backend'den al veya fallback kullan
      if (statsRes && statsRes.data) {
        setStats({
          totalSearches: statsRes.data.total_searches || 0,
          totalLinks: statsRes.data.recent_links || 0,
          uniqueDomains: statsRes.data.recent_unique_domains || 0
        })
      } else {
        // Fallback: eski yöntem
        try {
          const linksRes = await axios.get(`${API_BASE}/search/links/stats?days=30&limit=100`)
          const uniqueDomains = new Set(
            linksRes.data.map((link) => link.domain)
          ).size
          setStats({
            totalSearches: resultsRes.data.length,
            totalLinks: linksRes.data.reduce((sum, link) => sum + link.total_appearances, 0),
            uniqueDomains
          })
        } catch (fallbackError) {
          console.error('Fallback istatistik hatası:', fallbackError)
        }
      }
    } catch (error) {
      console.error('İstatistikler yüklenemedi:', error)
    } finally {
      setLoadingStats(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      await axios.put(`${API_BASE}/settings?site_id=${siteId}`, formData)
      setMessage({ type: 'success', text: 'Ayarlar başarıyla güncellendi!' })
      onUpdate()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Ayarlar güncellenirken hata oluştu'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleTestSearch = async () => {
    setLoading(true)
    setMessage(null)
    try {
      await axios.post(`${API_BASE}/search/run?site_id=${siteId}`)
      setMessage({ type: 'success', text: 'Test araması başlatıldı! Sonuçlar birkaç saniye içinde görünecektir.' })
      setTimeout(() => {
        fetchStats()
        onUpdate()
      }, 3000)
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Test araması başlatılırken hata oluştu'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Genel İstatistikler */}
      <div className="stats-grid" style={{ marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>📊 Toplam Arama</h3>
          <div className="value">{loadingStats ? '...' : stats.totalSearches}</div>
          <small style={{ color: '#666', fontSize: '12px' }}>Tüm zamanlar</small>
        </div>
        <div className="stat-card">
          <h3>🔗 Toplam Link</h3>
          <div className="value">{loadingStats ? '...' : stats.totalLinks}</div>
          <small style={{ color: '#666', fontSize: '12px' }}>Son 30 gün</small>
        </div>
        <div className="stat-card">
          <h3>🌐 Benzersiz Domain</h3>
          <div className="value">{loadingStats ? '...' : stats.uniqueDomains}</div>
          <small style={{ color: '#666', fontSize: '12px' }}>Son 30 gün</small>
        </div>
      </div>

      {/* Scheduler Durumu */}
      {schedulerStatus && (
        <div className="card" style={{ marginBottom: '20px', border: schedulerStatus.is_running && schedulerStatus.is_enabled ? '2px solid #10b981' : '2px solid #ef4444' }}>
          <h2>⏰ Otomatik Arama Durumu</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
            <div>
              <strong>Durum:</strong>
              <div style={{ 
                display: 'inline-block', 
                marginLeft: '10px',
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: schedulerStatus.is_running && schedulerStatus.is_enabled ? '#10b981' : '#ef4444',
                color: 'white',
                fontWeight: 'bold'
              }}>
                {schedulerStatus.is_running && schedulerStatus.is_enabled ? '✅ Aktif' : '❌ Pasif'}
              </div>
            </div>
            <div>
              <strong>Arama Sıklığı:</strong>
              <div style={{ marginTop: '5px', fontSize: '18px', fontWeight: 'bold' }}>
                {schedulerStatus.interval_hours} saatte bir
              </div>
              <small style={{ color: '#666', fontSize: '12px' }}>
                Günde {24 / schedulerStatus.interval_hours} kez
              </small>
            </div>
            {schedulerStatus.last_search_date && (
              <div>
                <strong>Son Arama:</strong>
                <div style={{ marginTop: '5px', fontSize: '14px' }}>
                  {formatInTimeZone(new Date(schedulerStatus.last_search_date), 'Europe/Istanbul', 'dd MMM yyyy HH:mm')} (TR)
                </div>
              </div>
            )}
            {schedulerStatus.next_run_time && (
              <div>
                <strong>Bir Sonraki Arama:</strong>
                <div style={{ marginTop: '5px', fontSize: '14px', color: '#667eea', fontWeight: 'bold' }}>
                  {formatInTimeZone(new Date(schedulerStatus.next_run_time), 'Europe/Istanbul', 'dd MMM yyyy HH:mm')} (TR)
                </div>
              </div>
            )}
          </div>
          {!schedulerStatus.is_running && schedulerStatus.is_enabled && (
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#fef3c7', borderRadius: '4px', color: '#92400e' }}>
              ⚠️ Scheduler ayarlı ancak çalışmıyor. Lütfen container'ı yeniden başlatın veya ayarları kontrol edin.
            </div>
          )}
          {!schedulerStatus.is_enabled && (
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#fee2e2', borderRadius: '4px', color: '#991b1b' }}>
              ⚠️ Otomatik arama devre dışı. Aşağıdaki ayarlardan etkinleştirebilirsiniz.
            </div>
          )}
        </div>
      )}

      {/* Son Aramalar */}
      {recentSearches.length > 0 && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h2>📋 Son Aramalar</h2>
          <table className="table" style={{ marginTop: '15px' }}>
            <thead>
              <tr>
                <th>Tarih</th>
                <th>Toplam Sonuç</th>
                <th>Link Sayısı</th>
              </tr>
            </thead>
            <tbody>
              {recentSearches.map((result) => (
                <tr key={result.id}>
                  <td>
                    {formatInTimeZone(new Date(result.search_date), 'Europe/Istanbul', 'dd MMM yyyy HH:mm')} (TR)
                  </td>
                  <td>{result.total_results?.toLocaleString() || 0}</td>
                  <td>{result.links?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Arama Ayarları Formu */}
      <div className="card">
        <h2>⚙️ Arama Ayarları</h2>
        <p style={{ color: '#666', marginBottom: '20px', fontSize: '14px' }}>
          Buradan arama parametrelerini yapılandırabilir ve otomatik aramayı kontrol edebilirsiniz.
        </p>

      {message && (
        <div
          className={`badge ${
            message.type === 'success' ? 'badge-success' : 'badge-danger'
          }`}
          style={{ marginBottom: '1rem', display: 'block', padding: '0.75rem' }}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>
            🔍 Aranacak Kelime(ler)
            <span style={{ marginLeft: '8px', fontSize: '12px', color: '#667eea', fontWeight: 'normal' }}>
              (Zorunlu)
            </span>
          </label>
          <input
            type="text"
            value={formData.search_query}
            onChange={(e) =>
              setFormData({ ...formData, search_query: e.target.value })
            }
            placeholder="padişah bet"
            required
          />
          <small style={{ color: '#666', display: 'block', marginTop: '0.5rem', lineHeight: '1.5' }}>
            💡 <strong>İpucu:</strong> Birden fazla kelime için virgülle ayırın. Örnek: "padişah bet, bahis sitesi, casino"
            <br />
            Her kelime için ayrı ayrı arama yapılacak ve sonuçlar birleştirilecektir.
          </small>
        </div>

        <div className="form-group">
          <label>
            🔑 SerpApi Key
            <span style={{ marginLeft: '8px', fontSize: '12px', color: '#667eea', fontWeight: 'normal' }}>
              (Zorunlu)
            </span>
          </label>
          <input
            type="password"
            value={formData.serpapi_key}
            onChange={(e) =>
              setFormData({ ...formData, serpapi_key: e.target.value })
            }
            placeholder="SerpApi API anahtarınızı girin"
            required
          />
          <small style={{ color: '#666', display: 'block', marginTop: '0.5rem', lineHeight: '1.5' }}>
            💡 <strong>İpucu:</strong> SerpApi key'inizi <a href="https://serpapi.com/dashboard" target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>serpapi.com/dashboard</a> adresinden alabilirsiniz.
            <br />
            Her site kendi SerpApi key'ini kullanır. Key'inizi güvenli tutun!
          </small>
        </div>

        <div className="form-group">
          <label>
            📍 Arama Konumu
          </label>
          <select
            value={formData.location}
            onChange={(e) =>
              setFormData({ ...formData, location: e.target.value })
            }
          >
            <option value="Fatih,Istanbul">Fatih, Istanbul</option>
            <option value="Istanbul">Istanbul (Genel)</option>
          </select>
          <small style={{ color: '#666', display: 'block', marginTop: '0.5rem' }}>
            Google aramalarının hangi konumdan yapılacağını belirler. Bu, sonuçları etkileyebilir.
          </small>
        </div>

        <div className="form-group">
          <label>
            ⏱️ Arama Aralığı (Saat)
          </label>
          <input
            type="number"
            value={formData.interval_hours}
            onChange={(e) =>
              setFormData({
                ...formData,
                interval_hours: parseInt(e.target.value) || 12
              })
            }
            min="1"
            max="24"
            required
          />
          <div style={{ 
            marginTop: '0.5rem', 
            padding: '10px', 
            backgroundColor: '#f0f9ff', 
            borderRadius: '4px',
            border: '1px solid #bae6fd'
          }}>
            <strong style={{ color: '#0369a1' }}>📊 Hesaplama:</strong>
            <ul style={{ margin: '5px 0 0 20px', color: '#0369a1', fontSize: '13px' }}>
              <li>Günde <strong>{24 / formData.interval_hours}</strong> kez arama yapılacak</li>
              <li>Haftada <strong>{(24 / formData.interval_hours) * 7}</strong> kez arama yapılacak</li>
              <li>Ayda <strong>{(24 / formData.interval_hours) * 30}</strong> kez arama yapılacak</li>
            </ul>
          </div>
        </div>

        <div className="form-group">
          <div className="checkbox-group" style={{ 
            padding: '15px', 
            backgroundColor: formData.enabled ? '#f0fdf4' : '#fef2f2',
            borderRadius: '8px',
            border: `2px solid ${formData.enabled ? '#10b981' : '#ef4444'}`
          }}>
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) =>
                setFormData({ ...formData, enabled: e.target.checked })
              }
              style={{ width: '20px', height: '20px', cursor: 'pointer' }}
            />
            <label htmlFor="enabled" style={{ marginBottom: 0, cursor: 'pointer', marginLeft: '10px', fontSize: '16px', fontWeight: 'bold' }}>
              {formData.enabled ? '✅ Otomatik arama aktif' : '❌ Otomatik arama pasif'}
            </label>
          </div>
          <small style={{ color: '#666', display: 'block', marginTop: '0.5rem' }}>
            {formData.enabled 
              ? 'Bot belirlediğiniz aralıklarla otomatik olarak arama yapacaktır.' 
              : 'Otomatik arama devre dışı. Sadece manuel test araması yapabilirsiniz.'}
          </small>
        </div>

        <div style={{ 
          display: 'flex', 
          gap: '1rem', 
          marginTop: '2rem',
          flexWrap: 'wrap'
        }}>
          <button 
            type="submit" 
            className="btn" 
            disabled={loading}
            style={{ flex: '1', minWidth: '200px' }}
          >
            {loading ? '⏳ Kaydediliyor...' : '💾 Ayarları Kaydet'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleTestSearch}
            disabled={loading}
            style={{ flex: '1', minWidth: '200px' }}
          >
            {loading ? '⏳ Çalışıyor...' : '🔍 Test Araması Yap'}
          </button>
        </div>
        
        <div style={{ 
          marginTop: '20px', 
          padding: '15px', 
          backgroundColor: '#f9fafb', 
          borderRadius: '8px',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ marginTop: 0, fontSize: '16px', color: '#374151' }}>ℹ️ Bilgilendirme</h3>
          <ul style={{ margin: '10px 0 0 20px', color: '#6b7280', fontSize: '14px', lineHeight: '1.8' }}>
            <li><strong>Ayarları Kaydet:</strong> Yaptığınız değişiklikleri kaydeder ve scheduler'ı günceller.</li>
            <li><strong>Test Araması:</strong> Ayarları kaydetmeden hemen bir arama yapar. Sonuçları Dashboard'da görebilirsiniz.</li>
            <li><strong>Otomatik Arama:</strong> Aktif olduğunda, bot belirlediğiniz aralıklarla otomatik arama yapar.</li>
            <li><strong>Veri Saklama:</strong> Tüm arama sonuçları ve link pozisyonları veritabanında saklanır.</li>
          </ul>
        </div>
      </form>
      </div>
    </div>
  )
}

export default Settings

