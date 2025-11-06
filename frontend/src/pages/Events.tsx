import { useState, useEffect } from 'react'
import { eventsApi, Event } from '../api/backend'
import './Events.css'

export default function Events() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadEvents()
  }, [])
  
  const loadEvents = async () => {
    try {
      const data = await eventsApi.list()
      setEvents(data)
    } catch (error) {
      console.error('Failed to load events:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return <div className="loading">Loading events...</div>
  }
  
  return (
    <div className="events-page">
      <h1>Events</h1>
      <div className="events-grid">
        {events.map(event => (
          <div key={event.event_id} className="event-card">
            {event.snapshot_path && (
              <img
                src={`http://localhost:8000${event.snapshot_path}`}
                alt={event.cls}
                className="event-snapshot"
              />
            )}
            <div className="event-info">
              <div className="event-header">
                <span className="event-class">{event.cls}</span>
                <span className="event-conf">{(event.conf * 100).toFixed(0)}%</span>
              </div>
              <div className="event-details">
                <div>Zone: {event.zone || 'None'}</div>
                <div>Model: {event.model}</div>
                <div>Time: {new Date(event.t_start * 1000).toLocaleString()}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

