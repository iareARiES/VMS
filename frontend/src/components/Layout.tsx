import { useState } from 'react'
import TopBar from './TopBar'
import LeftSidebar from './LeftSidebar'
import BottomBar from './BottomBar'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [currentTab, setCurrentTab] = useState<'live' | 'playback'>('live')

  return (
    <div className="vms-layout">
      <TopBar currentTab={currentTab} onTabChange={setCurrentTab} />
      <div className="vms-main">
        <LeftSidebar currentView={currentTab} />
        <div className="vms-content">
          {children}
        </div>
      </div>
      <BottomBar />
    </div>
  )
}
