import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Settings from './components/Settings'
import Dashboard from './components/Dashboard'
import Reports from './components/Reports'
import Charts from './components/Charts'
import Analytics from './components/Analytics'
import './App.css'

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [darkMode, setDarkMode] = useState(() => {
    // LocalStorage'dan dark mode tercihini al
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    fetchSettings()
  }, [])

  useEffect(() => {
    // Dark mode'u localStorage'a kaydet
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
    // Body'ye class ekle
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
  }, [darkMode])

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
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <img src="/logo.png" alt="Logo" style={{ height: '40px', width: 'auto' }} />
            Google Search Bot
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="dark-mode-toggle"
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
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
            className={activeTab === 'charts' ? 'active' : ''}
            onClick={() => setActiveTab('charts')}
          >
            Grafikler
          </button>
          <button
            className={activeTab === 'analytics' ? 'active' : ''}
            onClick={() => setActiveTab('analytics')}
          >
            Analitik
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
        {activeTab === 'charts' && <Charts API_BASE={API_BASE} />}
        {activeTab === 'analytics' && <Analytics API_BASE={API_BASE} />}
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

