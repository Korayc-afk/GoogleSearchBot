import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Analytics({ API_BASE }) {
  const [competitors, setCompetitors] = useState([])

  useEffect(() => {
    fetchCompetitors()
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

    </div>
  )
}

export default Analytics




