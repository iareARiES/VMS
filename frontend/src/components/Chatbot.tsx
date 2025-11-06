import { useState } from 'react'
import { queryApi } from '../api/backend'
import './Chatbot.css'

interface QueryResult {
  event_id: string
  cls: string
  conf: number
  t_start: number
  snapshot_path?: string
  bbox_xyxy: number[]
  zone?: string
  model?: string
}

export default function Chatbot() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<QueryResult[]>([])
  const [loading, setLoading] = useState(false)
  const [downloadFormat, setDownloadFormat] = useState<'zip' | 'json' | 'csv'>('zip')

  const parseQuery = (queryText: string): { object: string; startTime?: number; endTime?: number } => {
    // Parse queries like "find me person between 10:00 and 12:00"
    const lowerQuery = queryText.toLowerCase()
    const findMatch = lowerQuery.match(/find me (.+?)(?: between|$)/)
    const betweenMatch = lowerQuery.match(/between (.+?) and (.+?)(?:$| on| today)/)
    
    let object = 'person' // default
    if (findMatch) {
      object = findMatch[1].trim()
    }
    
    let startTime: number | undefined
    let endTime: number | undefined
    
    if (betweenMatch) {
      const startStr = betweenMatch[1].trim()
      const endStr = betweenMatch[2].trim()
      
      // Parse time strings (e.g., "10:00", "12:00")
      const parseTime = (timeStr: string): number => {
        const [hours, minutes] = timeStr.split(':').map(Number)
        const now = new Date()
        const date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours || 0, minutes || 0)
        return date.getTime() / 1000
      }
      
      try {
        startTime = parseTime(startStr)
        endTime = parseTime(endStr)
      } catch (e) {
        console.error('Failed to parse time:', e)
      }
    }
    
    return { object, startTime, endTime }
  }

  const handleQuery = async () => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const parsed = parseQuery(query)
      const data = await queryApi.query(
        parsed.object,
        parsed.startTime,
        parsed.endTime
      )
      setResults(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Query failed:', error)
      setResults([])
      alert('Query failed. Please check your query format.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadAll = async () => {
    if (results.length === 0) return

    try {
      const API_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:8000'
      
      if (downloadFormat === 'zip') {
        // Download as ZIP with images
        const response = await fetch(`${API_BASE}/api/events/export?format=zip&object=${results[0].cls}`)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `detections_${results[0].cls}_${Date.now()}.zip`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else if (downloadFormat === 'json') {
        // Download as JSON
        const jsonStr = JSON.stringify(results, null, 2)
        const blob = new Blob([jsonStr], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `detections_${Date.now()}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else if (downloadFormat === 'csv') {
        // Download as CSV
        const csvRows = [
          ['Event ID', 'Class', 'Confidence', 'Time', 'Zone', 'BBox'],
          ...results.map(r => [
            r.event_id,
            r.cls,
            (r.conf * 100).toFixed(2) + '%',
            new Date(r.t_start * 1000).toISOString(),
            r.zone || 'N/A',
            r.bbox_xyxy.join(',')
          ])
        ]
        const csv = csvRows.map(row => row.join(',')).join('\n')
        const blob = new Blob([csv], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `detections_${Date.now()}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please try again.')
    }
  }

  const drawBboxOnImage = (imageUrl: string, bbox: number[]): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve(imageUrl)
          return
        }
        
        ctx.drawImage(img, 0, 0)
        ctx.strokeStyle = '#ff0000'
        ctx.lineWidth = 3
        const [x1, y1, x2, y2] = bbox
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
        
        resolve(canvas.toDataURL())
      }
      img.onerror = () => resolve(imageUrl)
      img.src = imageUrl
    })
  }

  return (
    <div className="chatbot">
      <h2>Query Events</h2>
      <div className="chatbot-input">
        <input
          type="text"
          placeholder='e.g., "find me person between 10:00 and 12:00"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
        />
        <button onClick={handleQuery} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <>
          <div className="results-header">
            <span>Found {results.length} results</span>
            <div className="download-controls">
              <select
                value={downloadFormat}
                onChange={(e) => setDownloadFormat(e.target.value as 'zip' | 'json' | 'csv')}
                className="download-format-select"
              >
                <option value="zip">ZIP (with images)</option>
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
              </select>
              <button onClick={handleDownloadAll} className="download-btn">
                Download All ({downloadFormat.toUpperCase()})
              </button>
            </div>
          </div>
          <div className="results-gallery">
            {results.map((result) => (
              <div key={result.event_id} className="result-card">
                {result.snapshot_path && (
                  <div className="result-image-container">
                    <img
                      src={`http://localhost:8000${result.snapshot_path}`}
                      alt={result.cls}
                      className="result-image"
                      onLoad={(e) => {
                        const img = e.target as HTMLImageElement
                        drawBboxOnImage(img.src, result.bbox_xyxy).then(dataUrl => {
                          img.src = dataUrl
                        })
                      }}
                    />
                    <div className="bbox-overlay" style={{
                      position: 'absolute',
                      left: `${result.bbox_xyxy[0]}px`,
                      top: `${result.bbox_xyxy[1]}px`,
                      width: `${result.bbox_xyxy[2] - result.bbox_xyxy[0]}px`,
                      height: `${result.bbox_xyxy[3] - result.bbox_xyxy[1]}px`,
                      border: '2px solid #ff0000',
                      pointerEvents: 'none'
                    }}></div>
                  </div>
                )}
                <div className="result-info">
                  <div className="result-class">{result.cls}</div>
                  <div className="result-time">
                    {new Date(result.t_start * 1000).toLocaleString()}
                  </div>
                  {result.zone && (
                    <div className="result-zone">Zone: {result.zone}</div>
                  )}
                  {result.model && (
                    <div className="result-model">Model: {result.model}</div>
                  )}
                  <div className="result-conf">
                    Confidence: {(result.conf * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {!loading && results.length === 0 && query && (
        <div className="no-results">No results found</div>
      )}
    </div>
  )
}
