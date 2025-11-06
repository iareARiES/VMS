import { useState, useEffect } from 'react'
import { modelsApi, Model } from '../api/backend'
import './Models.css'

export default function Models() {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadModels()
  }, [])
  
  const loadModels = async () => {
    try {
      const data = await modelsApi.list()
      setModels(data)
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const toggleModel = async (name: string, enabled: boolean) => {
    try {
      await modelsApi.update(name, { enabled })
      await loadModels()
    } catch (error) {
      console.error('Failed to update model:', error)
    }
  }
  
  const updateConf = async (name: string, conf: number) => {
    try {
      await modelsApi.update(name, { conf })
      await loadModels()
    } catch (error) {
      console.error('Failed to update confidence:', error)
    }
  }
  
  const toggleClass = async (modelName: string, className: string, enabled: boolean) => {
    const model = models.find(m => m.name === modelName)
    if (!model) return
    
    const updatedClasses = {
      ...model.enabled_classes,
      [className]: enabled
    }
    
    try {
      await modelsApi.update(modelName, { enabled_classes: updatedClasses })
      await loadModels()
    } catch (error) {
      console.error('Failed to toggle class:', error)
    }
  }
  
  if (loading) {
    return <div className="loading">Loading models...</div>
  }
  
  return (
    <div className="models-page">
      <h1>Model Management</h1>
      
      <div className="models-grid">
        {models.map(model => (
          <div key={model.name} className="model-card">
            <div className="model-header">
              <h3>{model.name}</h3>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={model.enabled}
                  onChange={(e) => toggleModel(model.name, e.target.checked)}
                />
                <span>Enabled</span>
              </label>
            </div>
            
            <div className="model-info">
              <div className="info-row">
                <span>Type:</span>
                <span>{model.type}</span>
              </div>
              <div className="info-row">
                <span>Confidence:</span>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={model.conf}
                  onChange={(e) => updateConf(model.name, parseFloat(e.target.value))}
                />
              </div>
            </div>
            
            <div className="classes-section">
              <h4>Classes ({model.labels.length})</h4>
              <div className="classes-grid">
                {model.labels.map(cls => (
                  <label key={cls} className="class-toggle">
                    <input
                      type="checkbox"
                      checked={model.enabled_classes[cls] !== false}
                      onChange={(e) => toggleClass(model.name, cls, e.target.checked)}
                    />
                    <span>{cls}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

