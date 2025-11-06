import { useState, useEffect } from 'react'
import ZoneEditor from '../components/ZoneEditor'
import { zonesApi, Zone } from '../api/backend'
import './Zones.css'

export default function Zones() {
  const [zones, setZones] = useState<Zone[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadZones()
  }, [])
  
  const loadZones = async () => {
    try {
      const data = await zonesApi.list()
      setZones(data)
    } catch (error) {
      console.error('Failed to load zones:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSave = async (zone: Omit<Zone, 'zone_id'>) => {
    try {
      await zonesApi.create(zone)
      await loadZones()
    } catch (error) {
      console.error('Failed to save zone:', error)
    }
  }
  
  if (loading) {
    return <div className="loading">Loading zones...</div>
  }
  
  return (
    <div className="zones-page">
      <h1>Zone Setup</h1>
      <ZoneEditor zones={zones} onSave={handleSave} />
    </div>
  )
}

