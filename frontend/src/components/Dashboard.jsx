import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'
import { formatInTimeZone, utcToZonedTime } from 'date-fns-tz'

function Dashboard({ API_BASE }) {
  const [results, setResults] = useState([])
  const [linkStats, setLinkStats] = useState([])
  const [loading, setLoading] = useState(true)
  const [schedulerStatus, setSchedulerStatus] = useState(null)
  const [stats, setStats] = useState({
    totalSearches: 0,
    totalLinks: 0,
    uniqueDomains: 0
  })

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // 30 saniyede bir güncelle
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [resultsRes, linksRes, schedulerRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/search/results?limit=10`),
        axios.get(`${API_BASE}/search/links/stats?days=7&limit=10`),
        axios.get(`${API_BASE}/settings/scheduler-status`),
        axios.get(`${API_BASE}/search/stats`)
      ])

      setResults(resultsRes.data)
      setLinkStats(linksRes.data)
      setSchedulerStatus(schedulerRes.data)

      // İstatistikleri backend'den al
      setStats({
        totalSearches: statsRes.data.total_searches || 0,
        totalLinks: statsRes.data.recent_links || 0,
        uniqueDomains: statsRes.data.recent_unique_domains || 0
      })
    } catch (error) {
      console.error('Veri yüklenemedi:', error)
      // Hata durumunda eski yöntemle devam et
      try {
        const [resultsRes, linksRes, schedulerRes] = await Promise.all([
          axios.get(`${API_BASE}/search/results?limit=10`),
          axios.get(`${API_BASE}/search/links/stats?days=7&limit=10`),
          axios.get(`${API_BASE}/settings/scheduler-status`)
        ])

        setResults(resultsRes.data)
        setLinkStats(linksRes.data)
        setSchedulerStatus(schedulerRes.data)

        const uniqueDomains = new Set(
          linksRes.data.map((link) => link.domain)
        ).size

        setStats({
          totalSearches: resultsRes.data.length,
          totalLinks: linksRes.data.reduce((sum, link) => sum + link.total_appearances, 0),
          uniqueDomains
        })
      } catch (fallbackError) {
        console.error('Fallback veri yükleme hatası:', fallbackError)
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Yükleniyor...</div>
  }

  return (
    <div>
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
            </div>
            {schedulerStatus.last_search_date && (
              <div>
                <strong>Son Arama:</strong>
                <div style={{ marginTop: '5px', fontSize: '14px' }}>
                  {format(utcToZonedTime(new Date(schedulerStatus.last_search_date.endsWith('Z') ? schedulerStatus.last_search_date : schedulerStatus.last_search_date + 'Z'), 'Europe/Istanbul'), 'dd MMM yyyy HH:mm')} (TR)
                </div>
              </div>
            )}
            {schedulerStatus.next_run_time && (
              <div>
                <strong>Bir Sonraki Arama:</strong>
                <div style={{ marginTop: '5px', fontSize: '14px', color: '#667eea', fontWeight: 'bold' }}>
                  {format(utcToZonedTime(new Date(schedulerStatus.next_run_time.endsWith('Z') ? schedulerStatus.next_run_time : schedulerStatus.next_run_time + 'Z'), 'Europe/Istanbul'), 'dd MMM yyyy HH:mm')} (TR)
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
              ⚠️ Otomatik arama devre dışı. Ayarlar sayfasından etkinleştirebilirsiniz.
            </div>
          )}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <h3>📊 Toplam Arama</h3>
          <div className="value">{stats.totalSearches}</div>
          <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
            Tüm zamanlar
          </small>
        </div>
        <div className="stat-card">
          <h3>🔗 Toplam Link</h3>
          <div className="value">{stats.totalLinks}</div>
          <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
            Son 30 gün
          </small>
        </div>
        <div className="stat-card">
          <h3>🌐 Benzersiz Domain</h3>
          <div className="value">{stats.uniqueDomains}</div>
          <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
            Son 30 gün
          </small>
        </div>
      </div>

      <div className="card">
        <h2>📊 Son Arama Sonuçları</h2>
        {results.length === 0 ? (
          <p>Henüz arama sonucu yok. Ayarlar sayfasından test araması yapabilirsiniz.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Tarih</th>
                <th>Toplam Sonuç</th>
                <th>Link Sayısı</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.id}>
                  <td>
                    {format(utcToZonedTime(new Date(result.search_date.endsWith('Z') ? result.search_date : result.search_date + 'Z'), 'Europe/Istanbul'), 'dd MMM yyyy HH:mm')} (TR)
                  </td>
                  <td>{result.total_results.toLocaleString()}</td>
                  <td>{result.links?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>🔗 En Çok Görünen Linkler (Son 7 Gün)</h2>
        {linkStats.length === 0 ? (
          <p>Henüz link istatistiği yok.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Pozisyon</th>
                <th>Domain</th>
                <th>Başlık</th>
                <th>Görünme</th>
                <th>Aktif Gün</th>
                <th>Ort. Pozisyon</th>
              </tr>
            </thead>
            <tbody>
              {linkStats.map((link, idx) => (
                <tr key={idx}>
                  <td>
                    <span className="badge badge-success">
                      #{Math.round(link.average_position)}
                    </span>
                  </td>
                  <td>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: '#667eea' }}
                    >
                      {link.domain}
                    </a>
                  </td>
                  <td>{link.title || '-'}</td>
                  <td>{link.total_appearances}</td>
                  <td>{link.days_active}</td>
                  <td>{link.average_position.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Dashboard

