import './BottomBar.css'

interface BottomBarProps {
  currentTime?: number
  duration?: number
}

export default function BottomBar({ currentTime = 13, duration = 44 }: BottomBarProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="bottom-bar">
      <div className="progress-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        <div className="progress-text">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>
      
      <div className="controls">
        <button className="control-btn" title="Volume">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
          </svg>
        </button>
        <button className="control-btn">Video Source</button>
        <button className="control-btn">Stop All</button>
        <button className="control-btn">Stop</button>
        <button className="control-btn">Bookmark</button>
        <button className="control-btn">Refresh</button>
        <button className="control-btn">Audio Video Settings</button>
        <button className="control-btn" title="Microphone">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
          </svg>
        </button>
        <button className="control-btn next-btn">Next →</button>
      </div>
    </div>
  )
}

