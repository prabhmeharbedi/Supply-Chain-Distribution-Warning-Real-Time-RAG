import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  MapPin, 
  TrendingUp,
  Filter,
  Search
} from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import { Alert } from '../../types';

export default function RecentAlerts() {
  const { state, acknowledgeAlert } = useAppContext();
  const [filter, setFilter] = useState<'all' | 'unacknowledged' | 'critical'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAlerts = React.useMemo(() => {
    let alerts = [...state.alerts];

    // Apply filter
    switch (filter) {
      case 'unacknowledged':
        alerts = alerts.filter(alert => !alert.acknowledged);
        break;
      case 'critical':
        alerts = alerts.filter(alert => alert.severity === 'critical');
        break;
    }

    // Apply search
    if (searchQuery) {
      alerts = alerts.filter(alert =>
        alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.location.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return alerts.slice(0, 10); // Show only first 10
  }, [state.alerts, filter, searchQuery]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'warning': return 'text-orange-600 bg-orange-50';
      case 'watch': return 'text-blue-600 bg-blue-50';
      case 'info': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return AlertTriangle;
      case 'warning': return AlertTriangle;
      case 'watch': return Clock;
      case 'info': return TrendingUp;
      default: return AlertTriangle;
    }
  };

  const getTypeEmoji = (type: string) => {
    switch (type) {
      case 'weather': return '🌧️';
      case 'earthquake': return '🌍';
      case 'transport': return '🚛';
      case 'news': return '📰';
      case 'port': return '🚢';
      default: return '⚠️';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
          <p className="text-sm text-gray-500">Latest supply chain disruptions</p>
        </div>
        
        {/* Filter dropdown */}
        <div className="relative">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Alerts</option>
            <option value="unacknowledged">Unacknowledged</option>
            <option value="critical">Critical Only</option>
          </select>
          <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search alerts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Alerts list */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No alerts found matching your criteria</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const SeverityIcon = getSeverityIcon(alert.severity);
            
            return (
              <div
                key={alert.id}
                className={`
                  relative p-4 rounded-lg border transition-all duration-200 hover:shadow-md
                  ${alert.acknowledged 
                    ? 'border-gray-200 bg-gray-50 opacity-75' 
                    : 'border-gray-200 bg-white hover:border-gray-300'
                  }
                `}
              >
                {/* Severity indicator */}
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-transparent via-current to-transparent opacity-60"
                     style={{ color: getSeverityColor(alert.severity).includes('red') ? '#ef4444' :
                                     getSeverityColor(alert.severity).includes('orange') ? '#f97316' :
                                     getSeverityColor(alert.severity).includes('blue') ? '#3b82f6' : '#10b981' }} />

                <div className="flex items-start space-x-3">
                  {/* Icon and type */}
                  <div className="flex-shrink-0">
                    <div className={`p-2 rounded-lg ${getSeverityColor(alert.severity)}`}>
                      <SeverityIcon className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-lg">{getTypeEmoji(alert.type)}</span>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                            {alert.severity}
                          </span>
                          <span className="text-xs text-gray-500">
                            Confidence: {Math.round(alert.confidence * 100)}%
                          </span>
                        </div>
                        
                        <h4 className="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
                          {alert.title}
                        </h4>
                        
                        <div className="flex items-center text-xs text-gray-500 space-x-4 mb-2">
                          <div className="flex items-center">
                            <MapPin className="w-3 h-3 mr-1" />
                            <span className="truncate">{alert.location}</span>
                          </div>
                          <div className="flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                            <span>{formatTimeAgo(alert.createdAt)}</span>
                          </div>
                        </div>

                        <p className="text-xs text-gray-600 line-clamp-2 mb-3">
                          {alert.description}
                        </p>

                        {/* Impact info */}
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">
                            Impact: {alert.estimatedImpact}
                          </span>
                          <div className="flex items-center space-x-2">
                            {!alert.acknowledged && (
                              <button
                                onClick={() => acknowledgeAlert(alert.id)}
                                className="inline-flex items-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                              >
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Acknowledge
                              </button>
                            )}
                            {alert.acknowledged && (
                              <span className="inline-flex items-center text-xs text-green-600">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Acknowledged
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* View all link */}
      {filteredAlerts.length > 0 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
            View All Alerts →
          </button>
        </div>
      )}
    </div>
  );
}