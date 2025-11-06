import Chatbot from '../components/Chatbot'
import UploadVideo from '../components/UploadVideo'
import UploadImage from '../components/UploadImage'
import './Settings.css'

export default function Settings() {
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      <div className="settings-sections">
        <section className="settings-section">
          <UploadImage />
        </section>
        <section className="settings-section">
          <UploadVideo />
        </section>
        <section className="settings-section">
          <Chatbot />
        </section>
      </div>
    </div>
  )
}

