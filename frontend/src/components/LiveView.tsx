import { useRef, useEffect, useState } from 'react'
import { DetectionFrame } from '../api/sockets'
import './LiveView.css'

interface LiveViewProps {
  detections: DetectionFrame | null
}

export default function LiveView({ detections }: LiveViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    // Access device camera - use the same camera that detection service uses
    const startCamera = async () => {
      try {
        // Try to get camera with same constraints as detection service (index 0, typically default camera)
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            // Don't specify facingMode to use default camera (matches detection service camera 0)
          },
          audio: false
        })
        
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream
          setStream(mediaStream)
          setError(null)
        }
      } catch (err: any) {
        console.error('Error accessing camera:', err)
        setError(`Camera access denied: ${err.message}`)
        // Fallback: show placeholder - detection will still work but video won't show
      }
    }
    
    startCamera()
    
    return () => {
      // Cleanup stream on unmount
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])
  
  const drawDetections = () => {
    if (!canvasRef.current || !detections || !videoRef.current) return
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Get video display dimensions (what's actually shown on screen)
    const videoDisplayWidth = video.clientWidth
    const videoDisplayHeight = video.clientHeight
    
    // Set canvas size to match video display size
    canvas.width = videoDisplayWidth
    canvas.height = videoDisplayHeight
    
    // Calculate scaling factors (detection boxes are in detection source resolution, need to scale to display)
    // Prefer detection-provided dimensions when available
    const detectionWidth = (detections as any).width || videoNaturalWidth || 1280
    const detectionHeight = (detections as any).height || videoNaturalHeight || 720
    
    // Calculate scale factors for object-fit: contain behavior
    const scaleX = videoDisplayWidth / detectionWidth
    const scaleY = videoDisplayHeight / detectionHeight
    const scale = Math.min(scaleX, scaleY)  // Use smaller scale to maintain aspect ratio
    
    // Calculate offset to center the scaled content
    const offsetX = (videoDisplayWidth - detectionWidth * scale) / 2
    const offsetY = (videoDisplayHeight - detectionHeight * scale) / 2
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw bounding boxes
    if (detections.boxes && detections.boxes.length > 0) {
      detections.boxes.forEach(box => {
        const [x1, y1, x2, y2] = box.xyxy
        
        // Scale and offset coordinates
        const scaledX1 = x1 * scale + offsetX
        const scaledY1 = y1 * scale + offsetY
        const scaledX2 = x2 * scale + offsetX
        const scaledY2 = y2 * scale + offsetY
        const scaledWidth = scaledX2 - scaledX1
        const scaledHeight = scaledY2 - scaledY1
        
        // Draw box
        ctx.strokeStyle = box.event ? '#ff0000' : '#4a9eff'
        ctx.lineWidth = 3
        ctx.strokeRect(scaledX1, scaledY1, scaledWidth, scaledHeight)
        
        // Draw label background
        ctx.fillStyle = box.event ? '#ff0000' : '#4a9eff'
        ctx.font = `${Math.max(12, 14 * scale)}px monospace`
        const label = `${box.cls} ${(box.conf * 100).toFixed(0)}%`
        const textWidth = ctx.measureText(label).width
        ctx.fillRect(scaledX1, scaledY1 - 20, textWidth + 8, 20)
        
        // Draw label text
        ctx.fillStyle = '#fff'
        ctx.fillText(label, scaledX1 + 4, scaledY1 - 5)
        
        // Draw track ID
        if (box.id) {
          ctx.fillStyle = '#ffff00'
          ctx.font = `${Math.max(10, 12 * scale)}px monospace`
          ctx.fillText(`ID: ${box.id}`, scaledX1, scaledY2 + 15)
        }
        
        // Draw alert if intrusion
        if (box.event) {
          ctx.fillStyle = '#ff0000'
          ctx.font = `bold ${Math.max(14, 16 * scale)}px monospace`
          ctx.fillText('INTRUDER_ALERT', scaledX1, scaledY1 - 30)
        }
      })
    }
  }
  
  useEffect(() => {
    if (!detections) {
      // Clear canvas when detections are cleared
      const canvas = canvasRef.current
      const ctx = canvas?.getContext('2d') || null
      if (canvas && ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
      return
    }
    drawDetections()
  }, [detections])
  
  // Redraw on video resize
  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    
    const handleResize = () => {
      drawDetections()
    }
    
    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(video)
    
    return () => {
      resizeObserver.disconnect()
    }
  }, [detections])

  // Also listen for a global clearDetections event to immediately clear overlay
  useEffect(() => {
    const handler = () => {
      const canvas = canvasRef.current
      const ctx = canvas?.getContext('2d') || null
      if (canvas && ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    }
    window.addEventListener('clearDetections', handler as EventListener)
    return () => window.removeEventListener('clearDetections', handler as EventListener)
  }, [])
  
  return (
    <div className="live-view">
      <div className="video-container">
        {error ? (
          <div className="camera-error">
            <p>{error}</p>
            <p>Please allow camera access or connect a camera device</p>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="video-stream"
            />
            <canvas
              ref={canvasRef}
              className="overlay-canvas"
            />
          </>
        )}
      </div>
    </div>
  )
}
