export type AlertSeverity = 'critical' | 'warning' | 'watch' | 'info';
export type AlertType = 'weather' | 'earthquake' | 'news' | 'transport' | 'port';
export type SystemStatus = 'operational' | 'degraded' | 'down';

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  description: string;
  location: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  affectedRoutes: string[];
  estimatedImpact: string;
  confidence: number;
  createdAt: Date;
  acknowledged: boolean;
  recommendations: string[];
}

export interface DashboardStats {
  totalAlerts24h: number;
  criticalAlerts: number;
  activeDisruptions: number;
  systemHealth: SystemStatus;
  averageConfidence: number;
  topAffectedRoutes: string[];
}

export interface TimelineData {
  timestamp: string;
  critical: number;
  warning: number;
  watch: number;
  info: number;
}

export interface MapMarker {
  id: string;
  position: [number, number];
  severity: AlertSeverity;
  title: string;
  description: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  critical: boolean;
  warning: boolean;
  watch: boolean;
}