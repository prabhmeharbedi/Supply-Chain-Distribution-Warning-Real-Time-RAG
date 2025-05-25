import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface Alert {
  id: number;
  event_type: string;
  severity: 'critical' | 'warning' | 'watch' | 'info';
  title: string;
  description: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  confidence_score?: number;
  impact_score?: number;
  created_at: string;
  alert_score: number;
  priority_rank: number;
  should_alert: boolean;
  escalation_needed: boolean;
  acknowledged?: boolean;
}

export interface DashboardStats {
  total_alerts_24h: number;
  critical_alerts_24h: number;
  active_disruptions: number;
  affected_routes: string[];
  average_confidence: number;
  system_health: string;
}

export interface PathwayRAGResponse {
  query: string;
  response: string;
  sources: Array<{
    content: string;
    metadata: Record<string, any>;
    score: number;
  }>;
  processing_time: number;
  timestamp: string;
}

export interface RealTimeStats {
  total_documents: number;
  live_documents: number;
  recent_documents: number;
  queries_processed: number;
  average_response_time: number;
  last_update: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8001') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          // Don't redirect in demo mode
        }
        return Promise.reject(error);
      }
    );
  }

  // Health endpoints
  async getHealth() {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }

  async getPathwayHealth() {
    const response = await this.client.get('/api/v1/pathway-rag/health/pathway');
    return response.data;
  }

  // Alert endpoints
  async getAlerts(params?: {
    page?: number;
    page_size?: number;
    severity?: string[];
    hours_back?: number;
  }) {
    const response = await this.client.get('/api/v1/alerts', { params });
    return response.data;
  }

  async getAlert(id: number) {
    const response = await this.client.get(`/api/v1/alerts/${id}`);
    return response.data;
  }

  async acknowledgeAlert(id: number) {
    const response = await this.client.post(`/api/v1/alerts/${id}/acknowledge`);
    return response.data;
  }

  async getAlertSummary(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/alerts/summary/stats', {
      params: { hours_back }
    });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get('/api/v1/dashboard/stats');
    return response.data;
  }

  async getAlertTimeline(hours_back: number = 48) {
    const response = await this.client.get('/api/v1/dashboard/timeline', {
      params: { hours_back }
    });
    return response.data;
  }

  async getMapData(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/dashboard/map-data', {
      params: { hours_back }
    });
    return response.data;
  }

  async getSeverityDistribution(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/dashboard/severity-distribution', {
      params: { hours_back }
    });
    return response.data;
  }

  async getTopSources(hours_back: number = 24, limit: number = 10) {
    const response = await this.client.get('/api/v1/dashboard/top-sources', {
      params: { hours_back, limit }
    });
    return response.data;
  }

  // Pathway RAG endpoints
  async queryPathwayRAG(query: string): Promise<PathwayRAGResponse> {
    const response = await this.client.post('/api/v1/pathway-rag/query/real-time', {
      query
    });
    return response.data;
  }

  async addLiveData(data: {
    content: string;
    metadata?: Record<string, any>;
  }) {
    const response = await this.client.post('/api/v1/pathway-rag/data/add-live', data);
    return response.data;
  }

  async getRealTimeStats(): Promise<RealTimeStats> {
    const response = await this.client.get('/api/v1/pathway-rag/stats/real-time');
    return response.data;
  }

  async proveRealTimeCapability() {
    const response = await this.client.post('/api/v1/pathway-rag/demo/real-time-proof');
    return response.data;
  }

  // WebSocket connection for real-time updates
  createWebSocket(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    const wsUrl = this.client.defaults.baseURL?.replace('http', 'ws') + '/ws/real-time-updates';
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };
    
    return ws;
  }
}

export const apiClient = new ApiClient(); 