import axios from 'axios'

const API_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface Model {
  name: string
  type: string
  enabled: boolean
  conf: number
  iou: number
  labels: string[]
  enabled_classes: Record<string, boolean>
}

export interface Zone {
  zone_id: string
  name: string
  type: 'polygon' | 'tripwire'
  points: number[][]
  direction?: string
  allowed_classes: string[]
  min_size_px: number
  dwell_sec: number
  active_schedule?: any
  style: {
    stroke: string
    width: number
    opacity: number
  }
}

export interface Event {
  event_id: string
  camera_id: string
  model: string
  type: string
  zone?: string
  cls: string
  track_id?: number
  conf: number
  t_start: number
  t_end?: number
  snapshot_path?: string
  video_ref?: string
  bbox_xyxy: number[]
}

// Models API
export const modelsApi = {
  list: () => api.get<Model[]>('/api/models').then(r => r.data),
  update: (name: string, data: Partial<Model>) =>
    api.put(`/api/models/${name}`, data).then(r => r.data),
  upload: (file: File, type: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)
    return api.post('/api/models', formData).then(r => r.data)
  },
  delete: (name: string) => api.delete(`/api/models/${name}`).then(r => r.data)
}

// Zones API
export const zonesApi = {
  list: () => api.get<Zone[]>('/api/zones').then(r => r.data),
  create: (zone: Omit<Zone, 'zone_id'>) =>
    api.post<Zone>('/api/zones', zone).then(r => r.data),
  update: (zoneId: string, zone: Partial<Zone>) =>
    api.put<Zone>(`/api/zones/${zoneId}`, zone).then(r => r.data),
  delete: (zoneId: string) => api.delete(`/api/zones/${zoneId}`).then(r => r.data)
}

// Events API
export const eventsApi = {
  list: (params?: {
    zone?: string
    cls?: string
    model?: string
    t_start?: number
    t_end?: number
    limit?: number
    offset?: number
  }) => api.get<Event[]>('/api/events', { params }).then(r => r.data)
}

// Query API
export const queryApi = {
  query: (query: string, t_start?: number, t_end?: number) =>
    api.post('/api/query', { query, t_start, t_end }).then(r => r.data)
}

// SOS API
export const sosApi = {
  trigger: (eventId?: string) =>
    api.post('/api/sos', { action: 'trigger', event_id: eventId }).then(r => r.data),
  cancel: () =>
    api.post('/api/sos', { action: 'cancel' }).then(r => r.data)
}

// System API
export const systemApi = {
  health: () => api.get('/api/system/health').then(r => r.data),
  startDetection: () => api.post('/api/system/detection/start').then(r => r.data),
  stopDetection: () => api.post('/api/system/detection/stop').then(r => r.data)
}

