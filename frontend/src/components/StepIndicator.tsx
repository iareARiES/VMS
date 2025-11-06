import './StepIndicator.css'

interface StepIndicatorProps {
  currentStep: number
  steps: string[]
}

export default function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  return (
    <div className="step-indicator">
      {steps.map((step, index) => (
        <div key={index} className="step-group">
          <div className={`step ${index + 1 === currentStep ? 'active' : ''} ${index + 1 < currentStep ? 'completed' : ''}`}>
            <div className="step-number">{index + 1}</div>
            <div className="step-label">{step}</div>
          </div>
          {index < steps.length - 1 && (
            <div className={`step-arrow ${index + 1 < currentStep ? 'completed' : ''}`}>
              →
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

