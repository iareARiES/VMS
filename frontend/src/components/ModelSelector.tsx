import { useState, useEffect } from 'react'
import { modelsApi, Model, systemApi } from '../api/backend'
import './ModelSelector.css'

interface ModelSelectorProps {
  selectedModels: string[]
  onModelsChange: (models: string[]) => void
  onDetectionRestart?: () => void
  onEnabledModelsMetaChange?: (meta: { name: string; labels: string[] }[]) => void
  modelClassSelections?: Record<string, string[]> // model name -> selected classes
  onModelClassChange?: (modelName: string, classes: string[]) => void
}

export default function ModelSelector({ 
  selectedModels, 
  onModelsChange, 
  onDetectionRestart, 
  onEnabledModelsMetaChange,
  modelClassSelections = {},
  onModelClassChange
}: ModelSelectorProps) {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const modelList = await modelsApi.list()
      setModels(modelList)
      if (onEnabledModelsMetaChange) {
        const meta = modelList.filter(m => m.enabled).map(m => ({ name: m.name, labels: m.labels || [] }))
        onEnabledModelsMetaChange(meta)
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleModel = async (modelName: string, enabled: boolean) => {
    try {
      await modelsApi.update(modelName, { enabled })
      const updatedModels = models.map(m => 
        m.name === modelName ? { ...m, enabled } : m
      )
      setModels(updatedModels)
      if (onEnabledModelsMetaChange) {
        const meta = updatedModels.filter(m => m.enabled).map(m => ({ name: m.name, labels: m.labels || [] }))
        onEnabledModelsMetaChange(meta)
      }
      
      // Update selected models list
      let newSelectedModels: string[]
      if (enabled) {
        newSelectedModels = [...selectedModels, modelName]
      } else {
        newSelectedModels = selectedModels.filter(m => m !== modelName)
        // Clear class selections for disabled model
        if (onModelClassChange) {
          onModelClassChange(modelName, [])
        }
      }
      onModelsChange(newSelectedModels)
      
      // Don't auto-start detection here - let Dashboard handle it based on class selections
      // Just signal UI to clear existing boxes
      window.dispatchEvent(new CustomEvent('clearDetections'))
    } catch (error) {
      console.error('Failed to toggle model:', error)
    }
  }

  if (loading) {
    return <div className="model-selector-loading">Loading models...</div>
  }

  return (
    <div className="model-selector">
      <div className="model-selector-header">
        <h4>Available Models</h4>
        <span className="model-count">{models.length} models</span>
      </div>
      
      <div className="model-list">
        {models.map(model => (
          <div key={model.name} className="model-item">
            <label className="model-toggle">
              <input
                type="checkbox"
                checked={model.enabled}
                onChange={(e) => toggleModel(model.name, e.target.checked)}
              />
              <span className="model-name">{model.name}</span>
              <span className="model-type">{model.type}</span>
            </label>
            {model.enabled && (
              <div className="model-details">
                <div className="model-stat-row">
                  <div className="model-stat">
                    <span>Confidence:</span>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={model.conf}
                      onChange={(e) => {
                        modelsApi.update(model.name, { conf: parseFloat(e.target.value) })
                        loadModels()
                      }}
                      className="model-conf-input"
                    />
                  </div>
                  <div className="model-stat">
                    <span>Classes:</span>
                    <span className="model-classes-count">{model.labels.length}</span>
                  </div>
                </div>
                {onModelClassChange && (
                  <div className="model-class-selector">
                    <label>Select Classes for {model.name}:</label>
                    <div className="model-class-container">
                      {model.labels.map(label => {
                        const isSelected = (modelClassSelections[model.name] || []).includes(label)
                        return (
                          <label 
                            key={label} 
                            className={`model-class-checkbox ${isSelected ? 'selected' : ''}`}
                          >
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={(e) => {
                                const current = modelClassSelections[model.name] || []
                                let newSelection: string[]
                                if (e.target.checked) {
                                  newSelection = [...current, label]
                                } else {
                                  newSelection = current.filter(c => c !== label)
                                }
                                onModelClassChange(model.name, newSelection)
                              }}
                            />
                            <span>{label}</span>
                          </label>
                        )
                      })}
                    </div>
                    <div className="model-class-summary">
                      Selected: {modelClassSelections[model.name]?.length || 0} of {model.labels.length}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {models.length === 0 && (
        <div className="no-models">
          <p>No models found. Upload models in the Models page.</p>
        </div>
      )}
    </div>
  )
}

