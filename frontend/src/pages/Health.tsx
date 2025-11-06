import { useState, useEffect } from 'react'
import { systemApi } from '../api/backend'
import './Health.css'

export default function Health() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadHealth()
    const interval = setInterval(loadHealth, 5000)
    return () => clearInterval(interval)
  }, [])
  
  const loadHealth = async () => {
    try {
      const data = await systemApi.health()
      setHealth(data)
    } catch (error) {
      console.error('Failed to load health:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading || !health) {
    return <div className="loading">Loading health data...</div>
  }
  
  return (
    <div className="health-page">
      <h1>System Health</h1>
      <div className="health-grid">
        <div className="health-card">
          <div className="health-label">CPU Usage</div>
          <div className="health-value">{health.cpu_percent.toFixed(1)}%</div>
          <div className="health-bar">
            <div
              className="health-bar-fill"
              style={{ width: `${health.cpu_percent}%` }}
            />
          </div>
        </div>
        
        <div className="health-card">
          <div className="health-label">RAM Usage</div>
          <div className="health-value">{health.ram_percent.toFixed(1)}%</div>
          <div className="health-bar">
            <div
              className="health-bar-fill"
              style={{ width: `${health.ram_percent}%` }}
            />
          </div>
        </div>
        
        {health.temp_c && (
          <div className="health-card">
            <div className="health-label">Temperature</div>
            <div className="health-value">{health.temp_c.toFixed(1)}°C</div>
          </div>
        )}
        
        {health.fps && (
          <div className="health-card">
            <div className="health-label">FPS</div>
            <div className="health-value">{health.fps.toFixed(1)}</div>
          </div>
        )}
      </div>
    </div>
  )
}

