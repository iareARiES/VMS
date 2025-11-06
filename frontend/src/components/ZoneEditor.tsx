import { useState, useRef, useEffect } from 'react'
import { Zone } from '../api/backend'
import './ZoneEditor.css'

interface ZoneEditorProps {
  zones: Zone[]
  onSave: (zone: Omit<Zone, 'zone_id'>) => void
}

export default function ZoneEditor({ zones, onSave }: ZoneEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null)
  const [drawing, setDrawing] = useState(false)
  const [points, setPoints] = useState<number[][]>([])
  const [zoneName, setZoneName] = useState('')
  const [zoneType, setZoneType] = useState<'polygon' | 'tripwire'>('polygon')
  
  useEffect(() => {
    drawZones()
  }, [zones])
  
  const drawZones = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw existing zones
    zones.forEach(zone => {
      ctx.strokeStyle = zone.style.stroke
      ctx.lineWidth = zone.style.width
      ctx.globalAlpha = zone.style.opacity
      
      if (zone.type === 'polygon' && zone.points.length > 2) {
        ctx.beginPath()
        ctx.moveTo(zone.points[0][0], zone.points[0][1])
        zone.points.slice(1).forEach(p => ctx.lineTo(p[0], p[1]))
        ctx.closePath()
        ctx.stroke()
      } else if (zone.type === 'tripwire' && zone.points.length >= 2) {
        ctx.beginPath()
        ctx.moveTo(zone.points[0][0], zone.points[0][1])
        ctx.lineTo(zone.points[1][0], zone.points[1][1])
        ctx.stroke()
      }
    })
    
    ctx.globalAlpha = 1.0
    
    // Draw current points
    if (points.length > 0) {
      ctx.fillStyle = '#4a9eff'
      points.forEach((p, i) => {
        ctx.beginPath()
        ctx.arc(p[0], p[1], 5, 0, Math.PI * 2)
        ctx.fill()
        if (i > 0) {
          ctx.beginPath()
          ctx.moveTo(points[i - 1][0], points[i - 1][1])
          ctx.lineTo(p[0], p[1])
          ctx.strokeStyle = '#4a9eff'
          ctx.stroke()
        }
      })
    }
  }
  
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    if (zoneType === 'tripwire' && points.length >= 2) {
      return // Tripwire only needs 2 points
    }
    
    setPoints([...points, [x, y]])
  }
  
  const handleSave = () => {
    if (!zoneName || points.length < (zoneType === 'tripwire' ? 2 : 3)) {
      alert('Please provide a name and draw a valid zone')
      return
    }
    
    onSave({
      name: zoneName,
      type: zoneType,
      points: points,
      allowed_classes: [],
      min_size_px: 0,
      dwell_sec: 0,
      style: {
        stroke: '#ff0000',
        width: 2,
        opacity: 0.6
      }
    })
    
    setPoints([])
    setZoneName('')
  }
  
  useEffect(() => {
    drawZones()
  }, [points, zones])
  
  return (
    <div className="zone-editor">
      <div className="editor-controls">
        <input
          type="text"
          placeholder="Zone name"
          value={zoneName}
          onChange={(e) => setZoneName(e.target.value)}
        />
        <select value={zoneType} onChange={(e) => setZoneType(e.target.value as any)}>
          <option value="polygon">Polygon</option>
          <option value="tripwire">Tripwire</option>
        </select>
        <button onClick={handleSave}>Save Zone</button>
        <button onClick={() => setPoints([])}>Clear</button>
      </div>
      
      <canvas
        ref={canvasRef}
        width={1280}
        height={720}
        className="zone-canvas"
        onClick={handleCanvasClick}
      />
      
      <div className="zones-list">
        <h3>Existing Zones</h3>
        {zones.map(zone => (
          <div key={zone.zone_id} className="zone-item">
            <span>{zone.name}</span>
            <span className="zone-type">{zone.type}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

