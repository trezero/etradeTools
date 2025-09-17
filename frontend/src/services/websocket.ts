// WebSocket service for real-time updates


export type WebSocketEventType = 
  | 'connected'
  | 'new_decision'
  | 'feedback_updated'
  | 'preferences_updated'
  | 'portfolio_updated'
  | 'market_data_updated';

export interface WebSocketEvent {
  type: WebSocketEventType;
  data?: any;
  timestamp: Date;
}

export type WebSocketCallback = (event: WebSocketEvent) => void;


class WebSocketService {
  private socket: WebSocket | null = null;
  private callbacks: Map<WebSocketEventType, WebSocketCallback[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor() {
    this.initializeEventMap();
  }

  private initializeEventMap() {
    // Initialize callback arrays for each event type
    const eventTypes: WebSocketEventType[] = [
      'connected',
      'new_decision',
      'feedback_updated', 
      'preferences_updated',
      'portfolio_updated',
      'market_data_updated'
    ];

    eventTypes.forEach(type => {
      this.callbacks.set(type, []);
    });
  }

  connect(url: string = 'ws://localhost:8001/ws'): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('🔌 WebSocket already connected');
      return;
    }

    console.log(`🔌 Connecting to WebSocket: ${url}`);

    // For HTTP URLs, convert to WebSocket URL
    const wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://');
    
    try {
      // Create native WebSocket connection since our backend uses WebSocket, not Socket.IO
      this.connectNativeWebSocket(wsUrl);
    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      this.handleReconnect();
    }
  }

  private connectNativeWebSocket(url: string): void {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('connected', { connected: true });
    };

    ws.onmessage = (event) => {
      try {
        const message = event.data;
        console.log('📨 WebSocket message:', message);
        
        // Parse different message formats
        if (message === 'connected') {
          this.emit('connected', { connected: true });
        } else if (message.startsWith('new_decision:')) {
          const [, symbol, decisionType] = message.split(':');
          this.emit('new_decision', { symbol, decisionType });
        } else if (message.startsWith('feedback_updated:')) {
          const [, decisionId, feedback] = message.split(':');
          this.emit('feedback_updated', { decisionId, feedback });
        } else if (message === 'preferences_updated') {
          this.emit('preferences_updated', {});
        } else {
          // Try to parse as JSON
          try {
            const data = JSON.parse(message);
            this.emit('market_data_updated', data);
          } catch {
            console.log('📨 Raw message:', message);
          }
        }
      } catch (error) {
        console.error('❌ Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      console.log(`🔌 WebSocket disconnected: ${event.code} ${event.reason}`);
      this.handleReconnect();
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    // Store reference (cast to Socket for compatibility)
    this.socket = ws as any;
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  disconnect(): void {
    if (this.socket) {
      console.log('🔌 Disconnecting WebSocket');
      if (this.socket.close) {
        this.socket.close();
      } else if ((this.socket as any).disconnect) {
        (this.socket as any).disconnect();
      }
      this.socket = null;
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  on(eventType: WebSocketEventType, callback: WebSocketCallback): void {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      callbacks.push(callback);
    }
  }

  off(eventType: WebSocketEventType, callback: WebSocketCallback): void {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(eventType: WebSocketEventType, data?: any): void {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      const event: WebSocketEvent = {
        type: eventType,
        data,
        timestamp: new Date()
      };

      callbacks.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error(`❌ Error in WebSocket callback for ${eventType}:`, error);
        }
      });
    }
  }

  send(message: string): void {
    if (this.isConnected()) {
      if (this.socket && (this.socket as any).send) {
        (this.socket as any).send(message);
      }
    } else {
      console.warn('⚠️ Cannot send message: WebSocket not connected');
    }
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;