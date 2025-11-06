import { useState } from 'react'
import axios from 'axios'
import './UploadImage.css'

const API_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:8000'

export default function UploadImage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<any>(null)
  const [preview, setPreview] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      setResult(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)
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
        `${API_BASE}/api/upload/image`,
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
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-image">
      <h2>Upload Image for Analysis</h2>
      <div className="upload-form">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? 'Analyzing...' : 'Upload & Analyze'}
        </button>
      </div>

      {preview && (
        <div className="image-preview">
          <img src={preview} alt="Preview" />
        </div>
      )}

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
          <h3>{result.error ? 'Analysis Failed' : 'Analysis Complete'}</h3>
          {result.error ? (
            <p className="error">{result.error}</p>
          ) : (
            <>
              <p>Detections: {result.detections?.length || 0}</p>
              {result.detections && result.detections.length > 0 && (
                <div className="detections-list">
                  {result.detections.map((det: any, idx: number) => (
                    <div key={idx} className="detection-item">
                      <span className="det-class">{det.cls}</span>
                      <span className="det-conf">{(det.conf * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
              {result.annotated_image && (
                <div className="annotated-image">
                  <h4>Annotated Image:</h4>
                  <img src={`${API_BASE}${result.annotated_image}`} alt="Annotated" />
                  <a
                    href={`${API_BASE}${result.annotated_image}`}
                    download
                    className="download-btn"
                  >
                    Download Annotated Image
                  </a>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

