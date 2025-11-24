import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

function Reports({ API_BASE }) {
  const [activeTab, setActiveTab] = useState('daily')
  const [dailyReports, setDailyReports] = useState([])
  const [weeklyReports, setWeeklyReports] = useState([])
  const [monthlyReports, setMonthlyReports] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchReports()
  }, [activeTab])

  const fetchReports = async () => {
    setLoading(true)
    try {
      if (activeTab === 'daily') {
        const res = await axios.get(`${API_BASE}/search/reports/daily?days=30`)
        setDailyReports(res.data)
      } else if (activeTab === 'weekly') {
        const res = await axios.get(`${API_BASE}/search/reports/weekly?weeks=12`)
        setWeeklyReports(res.data)
      } else {
        const res = await axios.get(`${API_BASE}/search/reports/monthly?months=12`)
        setMonthlyReports(res.data)
      }
    } catch (error) {
      console.error('Raporlar yüklenemedi:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderReportTable = (reports, type) => {
    if (loading) {
      return <div className="loading">Yükleniyor...</div>
    }

    if (reports.length === 0) {
      return <p>Henüz rapor verisi yok.</p>
    }

    return (
      <table className="table">
        <thead>
          <tr>
            {type === 'daily' && <th>Tarih</th>}
            {type === 'weekly' && (
              <>
                <th>Hafta Başlangıç</th>
                <th>Hafta Bitiş</th>
              </>
            )}
            {type === 'monthly' && <th>Ay</th>}
            <th>Toplam Arama</th>
            <th>Benzersiz Link</th>
            <th>Top Linkler</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report, idx) => (
            <tr key={idx}>
              {type === 'daily' && (
                <td>
                  {format(new Date(report.date), 'dd MMM yyyy')}
                </td>
              )}
              {type === 'weekly' && (
                <>
                  <td>
                    {format(new Date(report.week_start), 'dd MMM yyyy')}
                  </td>
                  <td>
                    {format(new Date(report.week_end), 'dd MMM yyyy')}
                  </td>
                </>
              )}
              {type === 'monthly' && <td>{report.month}</td>}
              <td>{report.total_searches}</td>
              <td>{report.unique_links}</td>
              <td>
                <details>
                  <summary style={{ cursor: 'pointer', color: '#667eea' }}>
                    {report.top_links.length} link
                  </summary>
                  <div style={{ marginTop: '0.5rem', padding: '0.5rem' }}>
                    {report.top_links.slice(0, 5).map((link, linkIdx) => (
                      <div
                        key={linkIdx}
                        style={{
                          padding: '0.5rem',
                          marginBottom: '0.25rem',
                          background: '#f8f9fa',
                          borderRadius: '4px'
                        }}
                      >
                        <strong>{link.domain}</strong> - {link.total_appearances}{' '}
                        görünme
                        <br />
                        <small style={{ color: '#666' }}>
                          Ort. Pozisyon: {link.average_position.toFixed(1)} | Aktif
                          Gün: {link.days_active}
                        </small>
                      </div>
                    ))}
                  </div>
                </details>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button
            className={activeTab === 'daily' ? 'btn' : 'btn btn-secondary'}
            onClick={() => setActiveTab('daily')}
          >
            Günlük Raporlar
          </button>
          <button
            className={activeTab === 'weekly' ? 'btn' : 'btn btn-secondary'}
            onClick={() => setActiveTab('weekly')}
          >
            Haftalık Raporlar
          </button>
          <button
            className={activeTab === 'monthly' ? 'btn' : 'btn btn-secondary'}
            onClick={() => setActiveTab('monthly')}
          >
            Aylık Raporlar
          </button>
        </div>

        <h2>
          {activeTab === 'daily' && '📅 Günlük Raporlar'}
          {activeTab === 'weekly' && '📆 Haftalık Raporlar'}
          {activeTab === 'monthly' && '📊 Aylık Raporlar'}
        </h2>

        {activeTab === 'daily' && renderReportTable(dailyReports, 'daily')}
        {activeTab === 'weekly' && renderReportTable(weeklyReports, 'weekly')}
        {activeTab === 'monthly' && renderReportTable(monthlyReports, 'monthly')}
      </div>
    </div>
  )
}

export default Reports

