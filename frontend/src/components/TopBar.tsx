import { useState, useEffect } from 'react'
import { systemApi } from '../api/backend'
import SOSButton from './SOSButton'
import './TopBar.css'

interface TopBarProps {
  currentTab: 'live' | 'playback'
  onTabChange: (tab: 'live' | 'playback') => void
}

export default function TopBar({ currentTab, onTabChange }: TopBarProps) {
  const [dateTime, setDateTime] = useState(new Date())
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    const timer = setInterval(() => setDateTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const data = await systemApi.health()
        setHealth(data)
      } catch (error) {
        console.error('Failed to load health:', error)
      }
    }
    loadHealth()
    const interval = setInterval(loadHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  const formatDateTime = (date: Date) => {
    return date.toLocaleString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).replace(',', '')
  }

  return (
    <div className="top-bar">
      <div className="top-bar-info">
        <span className="app-title">(Version 1.0.0) VMS Client</span>
        <span className="separator">|</span>
        <span>Server: localhost</span>
        <span className="separator">|</span>
        <span>User: administrator</span>
        <span className="separator">|</span>
        <span>{formatDateTime(dateTime)}</span>
        <span className="separator">|</span>
        <span>CPU: {health?.cpu_percent?.toFixed(0) || 0}%</span>
        <span className="separator">|</span>
        <span>RAM: {health ? Math.round(health.ram_percent * 100 / 1024) : 0} MB</span>
      </div>
      
      <div className="top-bar-tabs">
        <button
          className={`tab ${currentTab === 'live' ? 'active' : ''}`}
          onClick={() => onTabChange('live')}
        >
          LiveView
        </button>
        <button
          className={`tab ${currentTab === 'playback' ? 'active' : ''}`}
          onClick={() => onTabChange('playback')}
        >
          PlayBack
        </button>
      </div>
      
      <div className="top-bar-title">
        <h2>Intrusion/Loitering Detection</h2>
      </div>
      
      <div className="top-bar-actions">
        <SOSButton />
      </div>
    </div>
  )
}

