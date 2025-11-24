import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Settings from './components/Settings'
import Dashboard from './components/Dashboard'
import Reports from './components/Reports'
import './App.css'

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/settings`)
      setSettings(response.data)
    } catch (error) {
      console.error('Ayarlar yüklenemedi:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 Google Search Bot</h1>
        <nav className="nav">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'reports' ? 'active' : ''}
            onClick={() => setActiveTab('reports')}
          >
            Raporlar
          </button>
          <button
            className={activeTab === 'settings' ? 'active' : ''}
            onClick={() => setActiveTab('settings')}
          >
            Ayarlar
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'dashboard' && <Dashboard API_BASE={API_BASE} />}
        {activeTab === 'reports' && <Reports API_BASE={API_BASE} />}
        {activeTab === 'settings' && (
          <Settings
            API_BASE={API_BASE}
            settings={settings}
            onUpdate={fetchSettings}
          />
        )}
      </main>
    </div>
  )
}

export default App

