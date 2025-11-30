import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Analytics({ API_BASE }) {
  const [filters, setFilters] = useState({
    domain: '',
    url_contains: '',
    min_position: '',
    max_position: '',
    start_date: '',
    end_date: '',
    days: 30
  })
  const [filteredLinks, setFilteredLinks] = useState([])
  const [competitors, setCompetitors] = useState([])
  const [topMovers, setTopMovers] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCompetitors()
    fetchTopMovers()
  }, [])

  const fetchCompetitors = async () => {
    try {
      const res = await axios.get(`${API_BASE}/analytics/competitor-analysis?days=30`).catch(() => ({ data: [] }))
      setCompetitors(Array.isArray(res.data) ? res.data : [])
    } catch (error) {
      console.error('Rakip analizi yüklenemedi:', error)
      setCompetitors([])
    }
  }

  const fetchTopMovers = async () => {
    try {
      const [upRes, downRes] = await Promise.all([
        axios.get(`${API_BASE}/analytics/top-movers?days=30&direction=up&limit=10`).catch(() => ({ data: [] })),
        axios.get(`${API_BASE}/analytics/top-movers?days=30&direction=down&limit=10`).catch(() => ({ data: [] }))
      ])
      setTopMovers({ 
        up: Array.isArray(upRes.data) ? upRes.data : [], 
        down: Array.isArray(downRes.data) ? downRes.data : [] 
      })
    } catch (error) {
      console.error('Top movers yüklenemedi:', error)
      setTopMovers({ up: [], down: [] })
    }
  }

  const handleFilter = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.domain) params.append('domain', filters.domain)
      if (filters.url_contains) params.append('url_contains', filters.url_contains)
      if (filters.min_position) params.append('min_position', filters.min_position)
      if (filters.max_position) params.append('max_position', filters.max_position)
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)
      params.append('days', filters.days)

      const res = await axios.get(`${API_BASE}/analytics/filter-links?${params.toString()}`)
      setFilteredLinks(res.data)
    } catch (error) {
      console.error('Filtreleme hatası:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFilters({
      domain: '',
      url_contains: '',
      min_position: '',
      max_position: '',
      start_date: '',
      end_date: '',
      days: 30
    })
    setFilteredLinks([])
  }

  return (
    <div>
      <div className="card">
        <h2>🔍 Gelişmiş Filtreleme</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div className="form-group">
            <label>Domain</label>
            <input
              type="text"
              value={filters.domain}
              onChange={(e) => setFilters({ ...filters, domain: e.target.value })}
              placeholder="example.com"
            />
          </div>
          <div className="form-group">
            <label>URL İçerir</label>
            <input
              type="text"
              value={filters.url_contains}
              onChange={(e) => setFilters({ ...filters, url_contains: e.target.value })}
              placeholder="kelime"
            />
          </div>
          <div className="form-group">
            <label>Min Pozisyon</label>
            <input
              type="number"
              value={filters.min_position}
              onChange={(e) => setFilters({ ...filters, min_position: e.target.value })}
              placeholder="1"
              min="1"
              max="10"
            />
          </div>
          <div className="form-group">
            <label>Max Pozisyon</label>
            <input
              type="number"
              value={filters.max_position}
              onChange={(e) => setFilters({ ...filters, max_position: e.target.value })}
              placeholder="10"
              min="1"
              max="10"
            />
          </div>
          <div className="form-group">
            <label>Başlangıç Tarihi</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Bitiş Tarihi</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn" onClick={handleFilter} disabled={loading}>
            {loading ? 'Filtreleniyor...' : '🔍 Filtrele'}
          </button>
          <button className="btn btn-secondary" onClick={handleReset}>
            🔄 Sıfırla
          </button>
        </div>
      </div>

      {filteredLinks.length > 0 && (
        <div className="card">
          <h2>📋 Filtrelenmiş Sonuçlar ({filteredLinks.length})</h2>
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Tarih</th>
                  <th>Domain</th>
                  <th>URL</th>
                  <th>Pozisyon</th>
                  <th>Başlık</th>
                </tr>
              </thead>
              <tbody>
                {filteredLinks.map((link) => (
                  <tr key={link.id}>
                    <td>{new Date(link.search_date).toLocaleString('tr-TR')}</td>
                    <td>{link.domain}</td>
                    <td>
                      <a href={link.url} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>
                        {link.url.substring(0, 50)}...
                      </a>
                    </td>
                    <td>
                      <span className="badge badge-success">#{link.position}</span>
                    </td>
                    <td>{link.title || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="card">
        <h2>🏆 Rakip Analizi</h2>
        {!competitors || competitors.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>Veri yok</p>
            <small style={{ display: 'block', marginTop: '10px' }}>
              Arama sonuçları oluştuktan sonra burada görünecektir.
            </small>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Domain</th>
                <th>Görünme</th>
                <th>Ort. Pozisyon</th>
                <th>En İyi</th>
                <th>En Kötü</th>
                <th>Benzersiz URL</th>
              </tr>
            </thead>
            <tbody>
              {competitors.map((comp, idx) => (
                <tr key={idx}>
                  <td><strong>{comp.domain}</strong></td>
                  <td>{comp.appearances}</td>
                  <td>#{comp.avg_position.toFixed(1)}</td>
                  <td>
                    <span className="badge badge-success">#{comp.best_position}</span>
                  </td>
                  <td>
                    <span className="badge badge-danger">#{comp.worst_position}</span>
                  </td>
                  <td>{comp.unique_urls}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h2>📈 En Çok Yükselenler</h2>
          {topMovers && topMovers.up && topMovers.up.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Değişim</th>
                </tr>
              </thead>
              <tbody>
                {topMovers.up.map((mover, idx) => (
                  <tr key={idx}>
                    <td><strong>{mover.domain || mover.url || '-'}</strong></td>
                    <td>
                      <span className="badge badge-success">
                        ↑ {Math.abs(mover.change || 0)} (#{mover.first_position || '-'} → #{mover.last_position || '-'})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              <p>Veri yok</p>
              <small style={{ display: 'block', marginTop: '10px' }}>
                En az 2 arama sonucu olması ve pozisyon yükselmesi olması gerekiyor.
              </small>
            </div>
          )}
        </div>

        <div className="card">
          <h2>📉 En Çok Düşenler</h2>
          {topMovers && topMovers.down && topMovers.down.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Değişim</th>
                </tr>
              </thead>
              <tbody>
                {topMovers.down.map((mover, idx) => (
                  <tr key={idx}>
                    <td><strong>{mover.domain || mover.url || '-'}</strong></td>
                    <td>
                      <span className="badge badge-danger">
                        ↓ {Math.abs(mover.change || 0)} (#{mover.first_position || '-'} → #{mover.last_position || '-'})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              <p>Veri yok</p>
              <small style={{ display: 'block', marginTop: '10px' }}>
                En az 2 arama sonucu olması ve pozisyon düşmesi olması gerekiyor.
              </small>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analytics




