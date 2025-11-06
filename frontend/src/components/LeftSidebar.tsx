import './LeftSidebar.css'

interface LeftSidebarProps {
  currentView?: string
}

export default function LeftSidebar({ currentView = 'live' }: LeftSidebarProps) {
  return (
    <div className="left-sidebar">
      <div className="view-controls">
        <div className="view-controls-header">
          <span>View Controls</span>
        </div>
        <div className="view-controls-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6M12 12h6m-6 0H6"/>
          </svg>
        </div>
      </div>
      
      <div className="live-views-section">
        <div className={`live-view-item ${currentView === 'live' ? 'active' : ''}`}>
          <span>Live Views</span>
        </div>
      </div>
    </div>
  )
}

