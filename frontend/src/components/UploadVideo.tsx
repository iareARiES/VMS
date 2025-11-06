import { useState } from 'react'
import axios from 'axios'
import './UploadVideo.css'

const API_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:8000'

export default function UploadVideo() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<any>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${API_BASE}/api/upload/video`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = (progressEvent.loaded / progressEvent.total) * 100
              setProgress(percent)
            }
          },
        }
      )
      setResult(response.data)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-video">
      <h2>Upload Video for Analysis</h2>
      <div className="upload-form">
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? 'Uploading...' : 'Upload & Analyze'}
        </button>
      </div>

      {uploading && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
          <span className="progress-text">{progress.toFixed(0)}%</span>
        </div>
      )}

      {result && (
        <div className="upload-result">
          <h3>{result.error ? 'Upload Failed' : 'Upload Complete'}</h3>
          {result.error ? (
            <p className="error">{result.error}</p>
          ) : (
            <>
              <p>Job ID: {result.job_id}</p>
              <p>Status: {result.message || result.status}</p>
              <p className="info">Analysis is running in the background. Check the Events page for results.</p>
            </>
          )}
        </div>
      )}
    </div>
  )
}

