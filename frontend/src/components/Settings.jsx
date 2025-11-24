import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Settings({ API_BASE, settings, onUpdate }) {
  const [formData, setFormData] = useState({
    search_query: '',
    location: 'Fatih,Istanbul',
    enabled: true,
    interval_hours: 12
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    if (settings) {
      setFormData({
        search_query: settings.search_query || '',
        location: settings.location || 'Fatih,Istanbul',
        enabled: settings.enabled !== undefined ? settings.enabled : true,
        interval_hours: settings.interval_hours || 12
      })
    }
  }, [settings])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      await axios.put(`${API_BASE}/settings`, formData)
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
      await axios.post(`${API_BASE}/search/run`)
      setMessage({ type: 'success', text: 'Test araması başarıyla çalıştırıldı!' })
      setTimeout(() => onUpdate(), 2000)
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Test araması sırasında hata oluştu'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>⚙️ Arama Ayarları</h2>

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
          <label>Aranacak Kelime</label>
          <input
            type="text"
            value={formData.search_query}
            onChange={(e) =>
              setFormData({ ...formData, search_query: e.target.value })
            }
            placeholder="padişah bet"
            required
          />
        </div>

        <div className="form-group">
          <label>Arama Konumu</label>
          <select
            value={formData.location}
            onChange={(e) =>
              setFormData({ ...formData, location: e.target.value })
            }
          >
            <option value="Fatih,Istanbul">Fatih, Istanbul</option>
            <option value="Istanbul">Istanbul (Genel)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Arama Aralığı (Saat)</label>
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
          <small style={{ color: '#666', display: 'block', marginTop: '0.25rem' }}>
            Günde {24 / formData.interval_hours} kez arama yapılacak
          </small>
        </div>

        <div className="form-group">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) =>
                setFormData({ ...formData, enabled: e.target.checked })
              }
            />
            <label htmlFor="enabled" style={{ marginBottom: 0, cursor: 'pointer' }}>
              Otomatik arama aktif
            </label>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleTestSearch}
            disabled={loading}
          >
            Test Araması Yap
          </button>
        </div>
      </form>
    </div>
  )
}

export default Settings

