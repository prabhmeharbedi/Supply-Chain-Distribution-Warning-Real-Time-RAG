import React from 'react';
import { useAppContext } from '../../contexts/AppContext';
import { 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Activity,
  Clock,
  MapPin,
  Users,
  Zap
} from 'lucide-react';

export default function Dashboard() {
  const { state } = useAppContext();

  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="bg-error-50 border border-error-200 rounded-lg p-4 m-6">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-error-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-error-800">Error</h3>
            <p className="mt-2 text-sm text-error-700">{state.error}</p>
          </div>
        </div>
      </div>
    );
  }

  const criticalAlerts = state.alerts.filter(a => a.severity === 'critical').length;
  const highAlerts = state.alerts.filter(a => a.severity === 'high').length;
  const acknowledgedAlerts = state.alerts.filter(a => a.acknowledged).length;
  const activeDisruptions = state.dashboardStats.activeDisruptions;

  return (
    <div className="p-6 space-y-6 bg-neutral-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Supply Chain Overview</h1>
          <p className="text-neutral-600 mt-1">Real-time monitoring and analytics</p>
        </div>
        <div className="flex items-center space-x-2 bg-success-50 border border-success-200 rounded-lg px-3 py-2">
          <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
          <span className="text-success-700 font-medium">Live Data</span>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Alerts */}
        <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6 hover:shadow-medium transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Total Alerts (24h)</p>
              <p className="text-3xl font-bold text-neutral-900">{state.dashboardStats.totalAlerts24h}</p>
            </div>
            <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Activity className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-success-500 mr-1" />
            <span className="text-success-600 font-medium">+12%</span>
            <span className="text-neutral-500 ml-1">vs yesterday</span>
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6 hover:shadow-medium transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Critical Alerts</p>
              <p className="text-3xl font-bold text-error-600">{criticalAlerts}</p>
            </div>
            <div className="h-12 w-12 bg-error-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-error-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-error-600 font-medium">Requires immediate attention</span>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6 hover:shadow-medium transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">System Health</p>
              <p className="text-3xl font-bold text-success-600 capitalize">{state.dashboardStats.systemHealth}</p>
            </div>
            <div className="h-12 w-12 bg-success-100 rounded-lg flex items-center justify-center">
              <Shield className="h-6 w-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div className="bg-success-500 h-2 rounded-full" style={{ width: '95%' }}></div>
            </div>
            <span className="text-success-600 font-medium ml-2">95%</span>
          </div>
        </div>

        {/* Average Confidence */}
        <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6 hover:shadow-medium transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Avg Confidence</p>
              <p className="text-3xl font-bold text-primary-600">{Math.round(state.dashboardStats.averageConfidence)}%</p>
            </div>
            <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Zap className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-primary-600 font-medium">ML Model Accuracy</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-soft border border-neutral-200">
          <div className="p-6 border-b border-neutral-200">
            <h3 className="text-lg font-semibold text-neutral-900">Recent Alerts</h3>
            <p className="text-neutral-600 text-sm">Latest supply chain disruptions</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {state.alerts.slice(0, 5).map((alert, index) => (
                <div key={alert.id} className="flex items-center space-x-4 p-4 bg-neutral-50 rounded-lg border border-neutral-100">
                  <div className={`w-3 h-3 rounded-full ${
                    alert.severity === 'critical' ? 'bg-error-500' :
                    alert.severity === 'high' ? 'bg-warning-500' :
                    alert.severity === 'medium' ? 'bg-accent-500' : 'bg-neutral-400'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{alert.title}</p>
                    <p className="text-sm text-neutral-600">{alert.location}</p>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-neutral-500">
                    <Clock className="h-3 w-3" />
                    <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="space-y-6">
          {/* Active Disruptions */}
          <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Active Disruptions</h3>
            <div className="text-center">
              <div className="text-4xl font-bold text-warning-600 mb-2">{activeDisruptions}</div>
              <p className="text-neutral-600">Ongoing incidents</p>
            </div>
          </div>

          {/* Top Affected Routes */}
          <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Top Affected Routes</h3>
            <div className="space-y-3">
              {state.dashboardStats.topAffectedRoutes.slice(0, 3).map((route, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-neutral-400" />
                    <span className="text-sm font-medium text-neutral-900">{route.name}</span>
                  </div>
                  <span className="text-sm text-error-600 font-medium">{route.impactLevel}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Banner */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold">Real-Time RAG Intelligence</h3>
            <p className="text-primary-100 mt-1">Powered by AI-driven supply chain analytics</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{acknowledgedAlerts}</div>
              <div className="text-primary-200 text-sm">Acknowledged</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{state.alerts.length - acknowledgedAlerts}</div>
              <div className="text-primary-200 text-sm">Pending</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}