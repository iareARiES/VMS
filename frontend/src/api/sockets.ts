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
      // Close existing connection if any
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
      
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        console.log(`✅ Connected to ${this.url}`)
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
        // Only log if not already closing/closed (to reduce spam)
        if (this.ws?.readyState !== WebSocket.CLOSING && this.ws?.readyState !== WebSocket.CLOSED) {
          console.warn(`WebSocket connection issue on ${this.url} (will retry)`)
        }
        if (this.onError) {
          this.onError(error)
        }
      }
      
      this.ws.onclose = (event) => {
        // Only log unexpected disconnections
        if (event.code !== 1000 && event.code !== 1001) {
          console.log(`Disconnected from ${this.url} (code: ${event.code})`)
        }
        this.reconnect()
      }
    } catch (error) {
      console.error(`Failed to create WebSocket connection to ${this.url}:`, error)
      this.reconnect()
    }
  }
  
  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
      if (this.reconnectAttempts <= 3) {  // Only log first few attempts
        console.log(`Reconnecting in ${delay}ms...`)
      }
      setTimeout(() => this.connect(), delay)
    } else {
      console.error(`Max reconnection attempts (${this.maxReconnectAttempts}) reached for ${this.url}`)
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

