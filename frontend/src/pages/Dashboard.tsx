import { useState, useEffect, useRef } from 'react'
import LiveView from '../components/LiveView'
import RightSidebar from '../components/RightSidebar'
import StepIndicator from '../components/StepIndicator'
import { WebSocketClient, DetectionFrame } from '../api/sockets'
import { systemApi, modelsApi } from '../api/backend'
import './Dashboard.css'

const CONFIG_STEPS = [
  'Step 1: Video Analytic Settings',
  'Step 2: Event Schedule Settings',
  'Step 3: Alert Settings and Finish'
]

export default function Dashboard() {
  const [fps, setFps] = useState(5)
  const [detections, setDetections] = useState<DetectionFrame | null>(null)
  const [isDetecting, setIsDetecting] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedClasses, setSelectedClasses] = useState<string[]>([])
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [modelClassSelections, setModelClassSelections] = useState<Record<string, string[]>>({}) // model name -> selected classes
  const [confidence, setConfidence] = useState(0.35)
  const [alertInterval, setAlertInterval] = useState(1)
  const [saveImage, setSaveImage] = useState(false)
  const [learningBased, setLearningBased] = useState(true)
  const wsRef = useRef<WebSocketClient | null>(null)
  const enabledModelsRef = useRef<string[]>([])
  const selectedClassesRef = useRef<string[]>([])
  const modelClassSelectionsRef = useRef<Record<string, string[]>>({})
  const [enabledModelsMeta, setEnabledModelsMeta] = useState<{ name: string; labels: string[] }[]>([])
  
  useEffect(() => {
    // Don't auto-start detection - wait for user to select models and classes
    // Detection will be started automatically when classes are selected (see useEffect for enabledModelsMeta)
    
    // Connect WebSocket
  const ws = new WebSocketClient(
      `ws://${window.location.hostname}:8000/ws/live`,
      (data: DetectionFrame) => {
        // Only process detection frames, ignore pings
        if (data.boxes !== undefined && data.fps !== undefined) {
          const currentEnabled = enabledModelsRef.current
          const modelClassSelections = modelClassSelectionsRef.current
          
          // Debug logging (only occasionally)
          if (data.frame_idx % 30 === 0) {
            console.log(`[Dashboard] Received ${data.boxes.length} boxes, Enabled models:`, currentEnabled, 'Class selections:', modelClassSelections)
          }
          
          // Filter boxes: only from enabled models AND only selected classes for that model
          let boxes = data.boxes.filter((b: any) => {
            // If box has a model name, check if model is enabled
            if (b.model) {
              if (!currentEnabled.includes(b.model)) {
                return false  // Model not enabled
              }
              // Check if classes are selected for this model
              const selectedClasses = modelClassSelections[b.model]
              if (!selectedClasses || selectedClasses.length === 0) {
                // No classes selected for this model - filter out
                if (data.frame_idx % 30 === 0) {
                  console.log(`[Dashboard] Filtered out ${b.cls} from ${b.model} (no classes selected for this model)`)
                }
                return false
              }
              // Check if this specific class is selected
              const isSelected = selectedClasses.includes(b.cls)
              if (!isSelected && data.frame_idx % 30 === 0) {
                console.log(`[Dashboard] Filtered out ${b.cls} from ${b.model} (not in selected classes: ${selectedClasses.join(', ')})`)
              }
              return isSelected
            }
            // If no model info, filter out (strict mode - require model info)
            return false
          })
          
          if (data.frame_idx % 30 === 0 && boxes.length > 0) {
            console.log(`[Dashboard] After filtering: ${boxes.length} boxes will be displayed`)
          }
          
          setDetections({ ...data, boxes })
          setFps(data.fps)
        }
      },
      (error) => {
        console.error('WebSocket connection error:', error)
      }
    )
    ws.connect()
    wsRef.current = ws
    
    return () => {
      ws.disconnect()
    }
  }, [])

  // Keep a live ref of enabled models for the WS callback to use
  useEffect(() => {
    enabledModelsRef.current = selectedModels
  }, [selectedModels])

  // Keep a live ref of selected classes for the WS callback to use
  useEffect(() => {
    selectedClassesRef.current = selectedClasses
  }, [selectedClasses])

  // Keep a live ref of model class selections
  useEffect(() => {
    modelClassSelectionsRef.current = modelClassSelections
  }, [modelClassSelections])

  // When enabled models or model class selections change, push to backend and restart detection
  useEffect(() => {
    if (enabledModelsMeta.length === 0) {
      // No models enabled, stop detection
      systemApi.stopDetection().catch(() => {})
      setDetections(null)
      return
    }
    
    const push = async () => {
      const modelSelections = modelClassSelectionsRef.current
      
      // Check if at least one model has at least one class selected
      const hasAnyClassSelected = enabledModelsMeta.some(m => {
        const selected = modelSelections[m.name] || []
        return selected.length > 0
      })
      
      if (!hasAnyClassSelected) {
        // No classes selected for any enabled model, stop detection
        try {
          await systemApi.stopDetection()
          setDetections(null)
        } catch {}
        return
      }
      
      // Update enabled_classes for each model based on model-specific selections
      const updates = enabledModelsMeta.map(async (m) => {
        const selected = modelSelections[m.name] || []
        const mapping: Record<string, boolean> = {}
        ;(m.labels || []).forEach(lbl => {
          mapping[lbl] = selected.includes(lbl)
        })
        try { 
          await modelsApi.update(m.name, { enabled_classes: mapping }) 
        } catch (e) {
          console.error(`Failed to update classes for ${m.name}:`, e)
        }
      })
      await Promise.all(updates)
      
      // Restart detection with new class selections
      try { 
        await systemApi.stopDetection() 
      } catch {}
      setTimeout(async () => {
        try { 
          await systemApi.startDetection() 
        } catch (e) {
          console.error('Failed to start detection:', e)
        }
      }, 300)
    }
    push()
  }, [enabledModelsMeta, modelClassSelections])

  // Clear detections when models are all disabled (signal from ModelSelector)
  useEffect(() => {
    const handler = () => setDetections(null)
    window.addEventListener('clearDetections', handler as EventListener)
    return () => window.removeEventListener('clearDetections', handler as EventListener)
  }, [])
  
  return (
    <div className="dashboard-vms">
      <StepIndicator currentStep={currentStep} steps={CONFIG_STEPS} />
      
      <div className="dashboard-main">
        <div className="video-section">
          <LiveView detections={detections} />
        </div>
        
        <RightSidebar
          selectedClasses={selectedClasses}
          onClassesChange={(classes) => {
            setSelectedClasses(classes)
            setDetections(null)
          }}
          selectedModels={selectedModels}
          onModelsChange={(models) => {
            setDetections(null)
            setSelectedModels(models)
            // Clear class selections for disabled models
            const newSelections = { ...modelClassSelections }
            Object.keys(newSelections).forEach(modelName => {
              if (!models.includes(modelName)) {
                delete newSelections[modelName]
              }
            })
            setModelClassSelections(newSelections)
          }}
          onDetectionRestart={() => {
            setIsDetecting(true)
            console.log('Detection restarted')
          }}
          onEnabledModelsMetaChange={(meta) => setEnabledModelsMeta(meta)}
          modelClassSelections={modelClassSelections}
          onModelClassChange={(modelName, classes) => {
            setModelClassSelections(prev => ({
              ...prev,
              [modelName]: classes
            }))
            setDetections(null)
          }}
          confidence={confidence}
          onConfidenceChange={setConfidence}
          alertInterval={alertInterval}
          onAlertIntervalChange={setAlertInterval}
          fps={fps}
          onFpsChange={setFps}
          saveImage={saveImage}
          onSaveImageChange={setSaveImage}
          learningBased={learningBased}
          onLearningBasedChange={setLearningBased}
        />
      </div>
    </div>
  )
}
