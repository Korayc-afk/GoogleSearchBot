import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a']

function Charts({ API_BASE, siteId = 'default' }) {
  const [positionTrend, setPositionTrend] = useState([])
  const [domainDistribution, setDomainDistribution] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUrl, setSelectedUrl] = useState('')

  useEffect(() => {
    fetchData()
  }, [selectedUrl, siteId])

  const fetchData = async () => {
    setLoading(true)
    try {
      const urlParam = selectedUrl ? `&url=${encodeURIComponent(selectedUrl)}` : ''
      const [trendRes, domainRes] = await Promise.all([
        axios.get(`${API_BASE}/analytics/position-trend?days=30&site_id=${siteId}${urlParam}`).catch(() => ({ data: { daily_data: {} } })),
        axios.get(`${API_BASE}/analytics/domain-distribution?days=30&limit=10&site_id=${siteId}`).catch(() => ({ data: [] }))
      ])

      // Position trend verilerini formatla
      const trendData = []
      if (trendRes.data && trendRes.data.daily_data) {
        Object.keys(trendRes.data.daily_data).sort().forEach(date => {
          const dayData = trendRes.data.daily_data[date]
          if (Array.isArray(dayData)) {
            dayData.forEach(item => {
              trendData.push({
                date: date,
                position: item.avg_position,
                domain: item.domain
              })
            })
          }
        })
      }
      setPositionTrend(trendData)

      // Domain distribution - boş array kontrolü
      setDomainDistribution(Array.isArray(domainRes.data) ? domainRes.data : [])
    } catch (error) {
      console.error('Grafik verileri yüklenemedi:', error)
      // Hata durumunda boş array'ler set et
      setPositionTrend([])
      setDomainDistribution([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Grafikler yükleniyor...</div>
  }

  return (
    <div>
      <div className="card">
        <h2>📈 Pozisyon Trend Grafiği</h2>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="URL filtrele (opsiyonel)"
            value={selectedUrl}
            onChange={(e) => setSelectedUrl(e.target.value)}
            style={{ padding: '0.5rem', width: '300px', borderRadius: '8px', border: '1px solid #ddd' }}
          />
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={positionTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis reversed domain={[1, 10]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="position" stroke="#667eea" strokeWidth={2} name="Ortalama Pozisyon" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>🥧 Domain Dağılımı</h2>
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={domainDistribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ domain, total_links }) => `${domain}: ${total_links}`}
              outerRadius={120}
              fill="#8884d8"
              dataKey="total_links"
            >
              {domainDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>📊 En Çok Görünen Domainler</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={domainDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="domain" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="total_links" fill="#667eea" name="Toplam Link" />
            <Bar dataKey="unique_urls" fill="#764ba2" name="Benzersiz URL" />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  )
}

export default Charts




