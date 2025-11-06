import { useState } from 'react'
import ModelSelector from './ModelSelector'
import './RightSidebar.css'

interface RightSidebarProps {
  selectedClasses: string[]
  onClassesChange: (classes: string[]) => void
  selectedModels: string[]
  onModelsChange: (models: string[]) => void
  onDetectionRestart?: () => void
  alertInterval: number
  onAlertIntervalChange: (value: number) => void
  fps: number
  onFpsChange: (value: number) => void
  modelClassSelections?: Record<string, string[]>
  onModelClassChange?: (modelName: string, classes: string[]) => void
  onEnabledModelsMetaChange?: (meta: { name: string; labels: string[] }[]) => void
}

const OBJECT_CLASSES = [
  'person', 'car', 'bicycle', 'motorbike', 'truck', 'bus',
  'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'fire', 'smoke'
]


export default function RightSidebar({
  selectedClasses,
  onClassesChange,
  selectedModels,
  onModelsChange,
  onDetectionRestart,
  alertInterval,
  onAlertIntervalChange,
  fps,
  onFpsChange,
  modelClassSelections = {},
  onModelClassChange,
  onEnabledModelsMetaChange
}: RightSidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    analytics: true,
    modelSelection: true,
    zoneSettings: false,
    shapeProps: false,
    schedules: false,
    alertSettings: false
  })

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <div className="right-sidebar">
      <div className="sidebar-header">
        <h3>Analytic Configuration</h3>
      </div>

      <div className="sidebar-content">
        {/* Analytics Grouped */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('analytics')}>
            <span>Analytics Grouped</span>
            <span className="toggle-icon">{expandedSections.analytics ? '−' : '+'}</span>
          </div>
          {expandedSections.analytics && (
            <div className="section-content">
              <div className="config-item">
                <label>Alert Interval</label>
                <select value={alertInterval} onChange={(e) => onAlertIntervalChange(parseFloat(e.target.value))}>
                  <option value={0.5}>0.5 Sec.</option>
                  <option value={1}>1 Sec.</option>
                  <option value={2}>2 Sec.</option>
                  <option value={5}>5 Sec.</option>
                  <option value={10}>10 Sec.</option>
                </select>
              </div>
              <div className="config-item">
                <label>FPS</label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={fps}
                  onChange={(e) => onFpsChange(parseInt(e.target.value))}
                />
              </div>
            </div>
          )}
        </div>

        {/* Model Selection */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('modelSelection')}>
            <span>Model Selection</span>
            <span className="toggle-icon">{expandedSections.modelSelection ? '−' : '+'}</span>
          </div>
          {expandedSections.modelSelection && (
            <div className="section-content">
              <ModelSelector
                selectedModels={selectedModels}
                onModelsChange={onModelsChange}
                onDetectionRestart={onDetectionRestart}
                onEnabledModelsMetaChange={(meta) => {
                  if (onEnabledModelsMetaChange) {
                    onEnabledModelsMetaChange(meta)
                  }
                  // When enabled models change, shrink selected classes to the union of enabled labels
                  const all = new Set<string>()
                  meta.forEach(m => (m.labels || []).forEach(l => all.add(l)))
                  const filtered = selectedClasses.filter(c => all.has(c))
                  if (filtered.length !== selectedClasses.length) {
                    onClassesChange(filtered)
                  }
                }}
                modelClassSelections={modelClassSelections}
                onModelClassChange={onModelClassChange}
              />
              <div className="config-hint" style={{ marginTop: '8px', fontSize: '11px' }}>
                Toggle models ON/OFF to enable detection. Multiple models can run simultaneously.
              </div>
            </div>
          )}
        </div>


        {/* Zone Settings */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('zoneSettings')}>
            <span>Zone Settings</span>
            <span className="toggle-icon">{expandedSections.zoneSettings ? '−' : '+'}</span>
          </div>
          {expandedSections.zoneSettings && (
            <div className="section-content">
              <div className="config-item">
                <label>Zone Type</label>
                <select defaultValue="restricted">
                  <option value="restricted">Restricted Zone</option>
                  <option value="buffer">Buffer Zone</option>
                  <option value="tripwire">Tripwire</option>
                  <option value="loitering">Loitering Zone</option>
                </select>
              </div>
              <div className="config-item">
                <label>Dwell Time (seconds)</label>
                <input type="number" min="0" step="0.5" defaultValue="0" />
              </div>
              <div className="config-item">
                <label>Min Object Size (px)</label>
                <input type="number" min="0" defaultValue="50" />
              </div>
              <div className="config-item">
                <label>Allowed Classes</label>
                <select multiple size={4}>
                  {OBJECT_CLASSES.map(obj => (
                    <option key={obj} value={obj} selected={obj === 'person'}>{obj}</option>
                  ))}
                </select>
                <div className="config-hint">Hold Ctrl/Cmd to select multiple</div>
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" defaultChecked />
                  Enable Zone Alerts
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Event Schedule Settings */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('schedules')}>
            <span>Event Schedule Settings</span>
            <span className="toggle-icon">{expandedSections.schedules ? '−' : '+'}</span>
          </div>
          {expandedSections.schedules && (
            <div className="section-content">
              <div className="config-item">
                <label>Schedule Type</label>
                <select defaultValue="always">
                  <option value="always">Always Active</option>
                  <option value="schedule">Time Schedule</option>
                  <option value="weekdays">Weekdays Only</option>
                  <option value="weekends">Weekends Only</option>
                </select>
              </div>
              <div className="config-item">
                <label>Start Time</label>
                <input type="time" defaultValue="00:00" />
              </div>
              <div className="config-item">
                <label>End Time</label>
                <input type="time" defaultValue="23:59" />
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" />
                  Enable Schedule
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Alert Settings */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('alertSettings')}>
            <span>Alert Settings</span>
            <span className="toggle-icon">{expandedSections.alertSettings ? '−' : '+'}</span>
          </div>
          {expandedSections.alertSettings && (
            <div className="section-content">
              <div className="config-item">
                <label>Alert Cooldown (seconds)</label>
                <input type="number" min="0" defaultValue="5" />
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" defaultChecked />
                  Enable Audio Alert
                </label>
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" />
                  Enable Webhook Notification
                </label>
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" />
                  Enable Email Notification
                </label>
              </div>
              <div className="config-item checkbox-item">
                <label>
                  <input type="checkbox" defaultChecked />
                  Auto-trigger SOS on Restricted Zone
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Selected Shape Properties */}
        <div className="config-section">
          <div className="section-header" onClick={() => toggleSection('shapeProps')}>
            <span>Selected Shape Properties</span>
            <span className="toggle-icon">{expandedSections.shapeProps ? '−' : '+'}</span>
          </div>
          {expandedSections.shapeProps && (
            <div className="section-content">
              <div className="config-item">
                <label>Zone Name</label>
                <input type="text" placeholder="Zone1" />
              </div>
              <div className="config-item">
                <label>Zone ID</label>
                <input type="text" readOnly value="zone_001" />
              </div>
            </div>
          )}
        </div>

        <button className="advance-prop-btn">Show Advance Prop.</button>
      </div>
    </div>
  )
}
