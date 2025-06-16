import { Alert, AlertSeverity, AlertType, DashboardStats, TimelineData, MapMarker } from '../types';
import { addHours, subHours, format } from 'date-fns';

class MockDataService {
  private alerts: Alert[] = [];
  private subscribers: ((alerts: Alert[]) => void)[] = [];

  constructor() {
    this.generateInitialData();
    this.startRealTimeUpdates();
  }

  private generateInitialData() {
    const locations = [
      { name: 'Los Angeles Port', coords: { lat: 33.7361, lng: -118.2639 } },
      { name: 'Shanghai Port', coords: { lat: 31.2304, lng: 121.4737 } },
      { name: 'Rotterdam Port', coords: { lat: 51.9244, lng: 4.4777 } },
      { name: 'Singapore Port', coords: { lat: 1.2966, lng: 103.8006 } },
      { name: 'Port of Long Beach', coords: { lat: 33.7701, lng: -118.2094 } },
      { name: 'Hamburg Port', coords: { lat: 53.5511, lng: 9.9937 } },
      { name: 'Antwerp Port', coords: { lat: 51.2211, lng: 4.4051 } },
      { name: 'Suez Canal', coords: { lat: 30.0444, lng: 32.3487 } },
      { name: 'Panama Canal', coords: { lat: 9.0820, lng: -79.7821 } },
      { name: 'Strait of Malacca', coords: { lat: 2.5, lng: 102.0 } },
    ];

    const eventTemplates = [
      {
        type: 'weather' as AlertType,
        titles: [
          'Hurricane approaching {location}',
          'Severe thunderstorms forecast for {location}',
          'Typhoon warning issued for {location} region',
          'Extreme weather conditions at {location}',
          'Flood warning for {location} area',
        ],
        descriptions: [
          'Major storm system expected to impact port operations and shipping routes.',
          'Severe weather conditions may cause delays in cargo handling and vessel movements.',
          'High winds and heavy rainfall could disrupt logistics operations.',
          'Extreme weather event requiring immediate attention to supply chain operations.',
        ],
        routes: ['Trans-Pacific', 'Asia-Europe', 'Trans-Atlantic'],
      },
      {
        type: 'earthquake' as AlertType,
        titles: [
          'Magnitude {mag} earthquake near {location}',
          'Seismic activity detected at {location}',
          'Earthquake warning for {location} region',
        ],
        descriptions: [
          'Seismic activity may affect port infrastructure and shipping operations.',
          'Earthquake could impact supply chain facilities and transportation networks.',
          'Infrastructure assessment required following seismic event.',
        ],
        routes: ['Pacific Rim', 'Ring of Fire', 'Asia-Pacific'],
      },
      {
        type: 'news' as AlertType,
        titles: [
          'Port workers strike at {location}',
          'Factory shutdown reported in {location}',
          'Trade dispute affects {location} operations',
          'Cyber attack disrupts {location} systems',
          'Equipment failure at {location}',
        ],
        descriptions: [
          'Labor dispute may cause significant delays in cargo processing.',
          'Industrial action could impact supply chain operations.',
          'Operational disruption affecting logistics and shipping schedules.',
          'Technical issues may cause delays in cargo handling.',
        ],
        routes: ['Multiple Routes', 'Regional Networks', 'Global Supply Chain'],
      },
    ];

    // Generate 50 historical alerts
    for (let i = 0; i < 50; i++) {
      const location = locations[Math.floor(Math.random() * locations.length)];
      const template = eventTemplates[Math.floor(Math.random() * eventTemplates.length)];
      const title = template.titles[Math.floor(Math.random() * template.titles.length)]
        .replace('{location}', location.name)
        .replace('{mag}', (Math.random() * 3 + 5).toFixed(1));
      
      const severity = this.getRandomSeverity();
      const confidence = Math.random() * 0.4 + 0.6; // 0.6 to 1.0

      this.alerts.push({
        id: `alert-${i + 1}`,
        type: template.type,
        severity,
        title,
        description: template.descriptions[Math.floor(Math.random() * template.descriptions.length)],
        location: location.name,
        coordinates: location.coords,
        affectedRoutes: template.routes.slice(0, Math.floor(Math.random() * 2) + 1),
        estimatedImpact: this.generateImpactEstimate(severity),
        confidence,
        createdAt: subHours(new Date(), Math.random() * 72), // Last 3 days
        acknowledged: Math.random() > 0.7,
        recommendations: this.generateRecommendations(severity, template.type),
      });
    }

    // Sort by creation date (newest first)
    this.alerts.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  private getRandomSeverity(): AlertSeverity {
    const severities: AlertSeverity[] = ['critical', 'warning', 'watch', 'info'];
    const weights = [0.05, 0.15, 0.35, 0.45]; // More info/watch, fewer critical
    
    const random = Math.random();
    let cumulativeWeight = 0;
    
    for (let i = 0; i < severities.length; i++) {
      cumulativeWeight += weights[i];
      if (random <= cumulativeWeight) {
        return severities[i];
      }
    }
    
    return 'info';
  }

  private generateImpactEstimate(severity: AlertSeverity): string {
    const impacts = {
      critical: ['$10M+ in delayed shipments', '$25M+ supply chain impact', 'Major route disruption'],
      warning: ['$2-5M in potential delays', '$1-3M operational impact', 'Moderate disruption expected'],
      watch: ['$500K-1M potential impact', 'Minor delays possible', 'Monitoring required'],
      info: ['Minimal impact expected', 'No immediate action required', 'Informational only'],
    };
    
    const options = impacts[severity];
    return options[Math.floor(Math.random() * options.length)];
  }

  private generateRecommendations(severity: AlertSeverity, type: AlertType): string[] {
    const recommendations: Record<AlertSeverity, string[]> = {
      critical: [
        'Activate emergency response protocols',
        'Contact affected suppliers immediately',
        'Implement contingency shipping routes',
        'Escalate to senior management',
        'Consider expedited shipping alternatives',
      ],
      warning: [
        'Monitor situation closely',
        'Prepare backup suppliers',
        'Review inventory levels',
        'Consider alternative routes',
        'Notify key stakeholders',
      ],
      watch: [
        'Continue monitoring',
        'Review contingency plans',
        'Maintain regular communication',
        'Assess potential impact',
      ],
      info: [
        'Archive for reference',
        'Share with relevant teams',
        'Monitor for updates',
      ],
    };

    return recommendations[severity].slice(0, Math.floor(Math.random() * 3) + 2);
  }

  private startRealTimeUpdates() {
    // Generate new alert every 30-120 seconds
    setInterval(() => {
      if (Math.random() > 0.3) { // 70% chance of new alert
        this.generateNewAlert();
      }
    }, (Math.random() * 90 + 30) * 1000);

    // Update existing alerts occasionally
    setInterval(() => {
      this.updateRandomAlert();
    }, 45000);
  }

  private generateNewAlert() {
    const locations = [
      { name: 'Los Angeles Port', coords: { lat: 33.7361, lng: -118.2639 } },
      { name: 'Shanghai Port', coords: { lat: 31.2304, lng: 121.4737 } },
      { name: 'Rotterdam Port', coords: { lat: 51.9244, lng: 4.4777 } },
      { name: 'Singapore Port', coords: { lat: 1.2966, lng: 103.8006 } },
      { name: 'Suez Canal', coords: { lat: 30.0444, lng: 32.3487 } },
    ];

    const newAlertTemplates = [
      'Real-time weather update for {location}',
      'Traffic congestion reported at {location}',
      'Vessel delay notification for {location}',
      'Customs processing delay at {location}',
      'Equipment maintenance at {location}',
    ];

    const location = locations[Math.floor(Math.random() * locations.length)];
    const title = newAlertTemplates[Math.floor(Math.random() * newAlertTemplates.length)]
      .replace('{location}', location.name);

    const newAlert: Alert = {
      id: `alert-${Date.now()}`,
      type: ['weather', 'transport', 'news'][Math.floor(Math.random() * 3)] as AlertType,
      severity: this.getRandomSeverity(),
      title,
      description: 'Real-time update on supply chain conditions affecting operations.',
      location: location.name,
      coordinates: location.coords,
      affectedRoutes: ['Trans-Pacific', 'Asia-Europe'][Math.floor(Math.random() * 2)] ? ['Trans-Pacific'] : ['Asia-Europe'],
      estimatedImpact: this.generateImpactEstimate(this.getRandomSeverity()),
      confidence: Math.random() * 0.4 + 0.6,
      createdAt: new Date(),
      acknowledged: false,
      recommendations: this.generateRecommendations(this.getRandomSeverity(), 'news'),
    };

    this.alerts.unshift(newAlert);
    
    // Keep only latest 100 alerts
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(0, 100);
    }

    this.notifySubscribers();
  }

  private updateRandomAlert() {
    if (this.alerts.length === 0) return;

    const randomIndex = Math.floor(Math.random() * Math.min(10, this.alerts.length));
    const alert = this.alerts[randomIndex];
    
    if (!alert.acknowledged && Math.random() > 0.8) {
      alert.acknowledged = true;
      this.notifySubscribers();
    }
  }

  private notifySubscribers() {
    this.subscribers.forEach(callback => callback([...this.alerts]));
  }

  // Public API
  getAlerts(): Alert[] {
    return [...this.alerts];
  }

  getAlert(id: string): Alert | undefined {
    return this.alerts.find(alert => alert.id === id);
  }

  acknowledgeAlert(id: string): void {
    const alert = this.alerts.find(a => a.id === id);
    if (alert) {
      alert.acknowledged = true;
      this.notifySubscribers();
    }
  }

  subscribeToUpdates(callback: (alerts: Alert[]) => void): () => void {
    this.subscribers.push(callback);
    return () => {
      const index = this.subscribers.indexOf(callback);
      if (index > -1) {
        this.subscribers.splice(index, 1);
      }
    };
  }

  getDashboardStats(): DashboardStats {
    const last24h = subHours(new Date(), 24);
    const recentAlerts = this.alerts.filter(alert => alert.createdAt > last24h);
    
    return {
      totalAlerts24h: recentAlerts.length,
      criticalAlerts: recentAlerts.filter(alert => alert.severity === 'critical').length,
      activeDisruptions: recentAlerts.filter(alert => 
        (alert.severity === 'critical' || alert.severity === 'warning') && !alert.acknowledged
      ).length,
      systemHealth: Math.random() > 0.1 ? 'operational' : 'degraded',
      averageConfidence: recentAlerts.reduce((sum, alert) => sum + alert.confidence, 0) / Math.max(recentAlerts.length, 1),
      topAffectedRoutes: ['Trans-Pacific', 'Asia-Europe', 'Trans-Atlantic'].slice(0, 3),
    };
  }

  getTimelineData(hours: number = 24): TimelineData[] {
    const data: TimelineData[] = [];
    const now = new Date();
    
    for (let i = hours; i >= 0; i--) {
      const timestamp = subHours(now, i);
      const hourStart = new Date(timestamp);
      hourStart.setMinutes(0, 0, 0);
      const hourEnd = addHours(hourStart, 1);
      
      const hourAlerts = this.alerts.filter(alert => 
        alert.createdAt >= hourStart && alert.createdAt < hourEnd
      );
      
      data.push({
        timestamp: format(hourStart, 'HH:mm'),
        critical: hourAlerts.filter(a => a.severity === 'critical').length,
        warning: hourAlerts.filter(a => a.severity === 'warning').length,
        watch: hourAlerts.filter(a => a.severity === 'watch').length,
        info: hourAlerts.filter(a => a.severity === 'info').length,
      });
    }
    
    return data;
  }

  getMapMarkers(): MapMarker[] {
    const recentAlerts = this.alerts
      .filter(alert => alert.coordinates && subHours(new Date(), 24) < alert.createdAt)
      .slice(0, 20);
    
    return recentAlerts.map(alert => ({
      id: alert.id,
      position: [alert.coordinates!.lat, alert.coordinates!.lng] as [number, number],
      severity: alert.severity,
      title: alert.title,
      description: alert.description,
    }));
  }
}

export const mockDataService = new MockDataService();