import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

function Dashboard({ API_BASE }) {
  const [results, setResults] = useState([])
  const [linkStats, setLinkStats] = useState([])
  const [loading, setLoading] = useState(true)
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
      const [resultsRes, linksRes] = await Promise.all([
        axios.get(`${API_BASE}/search/results?limit=10`),
        axios.get(`${API_BASE}/search/links/stats?days=7&limit=10`)
      ])

      setResults(resultsRes.data)
      setLinkStats(linksRes.data)

      // İstatistikleri hesapla
      const uniqueDomains = new Set(
        linksRes.data.map((link) => link.domain)
      ).size

      setStats({
        totalSearches: resultsRes.data.length,
        totalLinks: linksRes.data.reduce((sum, link) => sum + link.total_appearances, 0),
        uniqueDomains
      })
    } catch (error) {
      console.error('Veri yüklenemedi:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Yükleniyor...</div>
  }

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Toplam Arama</h3>
          <div className="value">{stats.totalSearches}</div>
        </div>
        <div className="stat-card">
          <h3>Toplam Link</h3>
          <div className="value">{stats.totalLinks}</div>
        </div>
        <div className="stat-card">
          <h3>Benzersiz Domain</h3>
          <div className="value">{stats.uniqueDomains}</div>
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
                    {format(new Date(result.search_date), 'dd MMM yyyy HH:mm')}
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

