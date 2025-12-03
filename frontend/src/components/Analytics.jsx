import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Analytics({ API_BASE }) {
  const [competitors, setCompetitors] = useState([])
  const [topMovers, setTopMovers] = useState([])

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

  return (
    <div>
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




