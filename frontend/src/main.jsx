import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, useParams, Navigate } from 'react-router-dom'
import App from './App'
import './index.css'

function AppWithSite() {
  const { siteId } = useParams()
  return <App siteId={siteId} />
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/default" replace />} />
        <Route path="/:siteId" element={<AppWithSite />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)




