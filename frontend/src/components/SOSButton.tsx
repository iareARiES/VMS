import { useState } from 'react'
import { sosApi } from '../api/backend'
import './SOSButton.css'

export default function SOSButton() {
  const [sosActive, setSosActive] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  
  const handleSOS = async () => {
    if (sosActive) {
      // Cancel SOS
      try {
        await sosApi.cancel()
        setSosActive(false)
        setShowConfirm(false)
      } catch (error) {
        console.error('Failed to cancel SOS:', error)
        alert('Failed to cancel SOS')
      }
    } else {
      // Show confirmation before triggering
      setShowConfirm(true)
    }
  }

  const confirmSOS = async () => {
    try {
      await sosApi.trigger()
      setSosActive(true)
      setShowConfirm(false)
      // Play alert sound
      playAlertSound()
    } catch (error) {
      console.error('Failed to trigger SOS:', error)
      alert('Failed to trigger SOS')
      setShowConfirm(false)
    }
  }

  const cancelConfirm = () => {
    setShowConfirm(false)
  }

  const playAlertSound = () => {
    // Create audio context for alert sound
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.value = 800
    oscillator.type = 'sine'
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  }

  return (
    <>
      <button
        className={`sos-button ${sosActive ? 'active' : ''}`}
        onClick={handleSOS}
      >
        {sosActive ? 'CANCEL SOS' : 'SOS'}
      </button>
      
      {showConfirm && (
        <div className="sos-confirm-overlay">
          <div className="sos-confirm-dialog">
            <h3>Confirm SOS Alert</h3>
            <p>Are you sure you want to trigger an SOS alert?</p>
            <div className="sos-confirm-buttons">
              <button className="sos-confirm-btn confirm" onClick={confirmSOS}>
                Confirm SOS
              </button>
              <button className="sos-confirm-btn cancel" onClick={cancelConfirm}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
