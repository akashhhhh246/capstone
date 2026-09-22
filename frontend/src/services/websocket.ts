import { SimulationEventPayload } from '../types';

type EventCallback = (event: SimulationEventPayload) => void;
type StatusCallback = (connected: boolean) => void;
type ControlCallback = (type: string, payload: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: Set<EventCallback> = new Set();
  private statusListeners: Set<StatusCallback> = new Set();
  private controlListeners: Set<ControlCallback> = new Set();
  private isConnected = false;
  private simulationId = 'global';
  private reconnectTimer: any = null;

  connect(simulationId = 'global') {
    this.simulationId = simulationId;
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/api/v1/ws/simulation/${simulationId}`;

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.isConnected = true;
        this.notifyStatus(true);
        console.log(`[WS] Connected to simulation channel: ${simulationId}`);
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'SIMULATION_PROPAGATION_EVENT' && message.data) {
            this.notifyListeners(message.data);
          } else if (message.type) {
            this.notifyControlListeners(message.type, message);
          }
        } catch (e) {
          console.warn('[WS] Non-JSON payload received:', event.data);
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.notifyStatus(false);
        this.scheduleReconnect();
      };

      this.socket.onerror = (err) => {
        console.warn('[WS] Error:', err);
        this.socket?.close();
      };
    } catch (e) {
      console.error('[WS] Connection exception:', e);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect(this.simulationId);
    }, 3000);
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
    this.notifyStatus(false);
  }

  subscribe(callback: EventCallback) {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  onStatusChange(callback: StatusCallback) {
    this.statusListeners.add(callback);
    callback(this.isConnected);
    return () => {
      this.statusListeners.delete(callback);
    };
  }

  onControl(callback: ControlCallback) {
    this.controlListeners.add(callback);
    return () => {
      this.controlListeners.delete(callback);
    };
  }

  private notifyControlListeners(type: string, payload: any) {
    this.controlListeners.forEach((cb) => {
      try {
        cb(type, payload);
      } catch (err) {
        console.error('[WS] Control listener error:', err);
      }
    });
  }

  private notifyListeners(data: SimulationEventPayload) {
    this.listeners.forEach((listener) => {
      try {
        listener(data);
      } catch (err) {
        console.error('[WS] Listener execution error:', err);
      }
    });
  }

  private notifyStatus(status: boolean) {
    this.statusListeners.forEach((listener) => {
      try {
        listener(status);
      } catch (err) {
        console.error('[WS] Status listener error:', err);
      }
    });
  }
}

export const wsService = new WebSocketService();
