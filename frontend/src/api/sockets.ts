export interface DetectionFrame {
  ts: number
  frame_idx: number
  boxes: Array<{
    id: number
    cls: string
    conf: number
    xyxy: [number, number, number, number]
    model?: string
    zone?: string
    event?: string
  }>
  fps: number
  width?: number
  height?: number
}

export interface Alert {
  event_id: string
  type: string
  zone: string
  cls: string
  track_id: number
  t_start: number
  snapshot: string
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  constructor(
    private url: string,
    private onMessage: (data: any) => void,
    private onError?: (error: Event) => void
  ) {}
  
  connect() {
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        console.log(`Connected to ${this.url}`)
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // Ignore ping messages
          if (data.type === 'ping') {
            return
          }
          this.onMessage(data)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error(`WebSocket error on ${this.url}:`, error)
        if (this.onError) {
          this.onError(error)
        }
      }
      
      this.ws.onclose = () => {
        console.log(`Disconnected from ${this.url}`)
        this.reconnect()
      }
    } catch (error) {
      console.error(`Failed to connect to ${this.url}:`, error)
      this.reconnect()
    }
  }
  
  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
      console.log(`Reconnecting in ${delay}ms...`)
      setTimeout(() => this.connect(), delay)
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
  
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

