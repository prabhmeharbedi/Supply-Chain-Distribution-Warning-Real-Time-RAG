import React, { useMemo } from 'react';
import { MapPin, Layers, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';

export default function AlertsMap() {
  const { state } = useAppContext();
  
  const mapMarkers = useMemo(() => {
    return state.alerts
      .filter(alert => alert.coordinates)
      .slice(0, 20) // Limit to 20 most recent alerts
      .map(alert => ({
        id: alert.id,
        position: alert.coordinates,
        severity: alert.severity,
        title: alert.title,
        location: alert.location,
        type: alert.type,
        createdAt: alert.createdAt
      }));
  }, [state.alerts]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f97316';
      case 'watch': return '#3b82f6';
      case 'info': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'weather': return '🌧️';
      case 'earthquake': return '🌍';
      case 'transport': return '🚛';
      case 'news': return '📰';
      case 'port': return '🚢';
      default: return '⚠️';
    }
  };

  // Mock world map SVG (simplified for demo)
  const worldMapPaths = [
    // North America
    "M158,150 L180,140 L220,145 L240,150 L235,180 L200,190 L170,185 L155,165 Z",
    // Europe
    "M280,130 L320,125 L340,135 L335,155 L310,160 L285,150 Z",
    // Asia
    "M340,120 L420,115 L450,125 L445,165 L400,170 L345,160 Z",
    // Africa
    "M280,160 L320,155 L340,170 L350,220 L320,235 L285,225 L275,190 Z",
    // South America
    "M200,200 L230,195 L240,220 L235,260 L210,270 L190,250 L185,220 Z",
    // Australia
    "M420,220 L450,215 L460,230 L455,240 L425,245 L415,235 Z"
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Global Disruption Map</h3>
          <p className="text-sm text-gray-500">Real-time alert locations • Last 24 hours</p>
        </div>
        
        {/* Map controls */}
        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Layers className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <ZoomOut className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="relative bg-gradient-to-b from-blue-50 to-blue-100 rounded-lg overflow-hidden" style={{ height: '400px' }}>
        {/* World map background */}
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 600 300"
          style={{ background: 'linear-gradient(to bottom, #dbeafe, #bfdbfe)' }}
        >
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e7ff" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Continents */}
          {worldMapPaths.map((path, index) => (
            <path
              key={index}
              d={path}
              fill="#10b981"
              fillOpacity="0.6"
              stroke="#059669"
              strokeWidth="1"
            />
          ))}
          
          {/* Alert markers */}
          {mapMarkers.map((marker, index) => {
            // Convert lat/lng to SVG coordinates (simplified projection)
            const x = ((marker.position[0] + 180) / 360) * 600;
            const y = ((90 - marker.position[1]) / 180) * 300;
            
            return (
              <g key={marker.id}>
                {/* Marker pulse animation */}
                <circle
                  cx={x}
                  cy={y}
                  r="8"
                  fill={getSeverityColor(marker.severity)}
                  fillOpacity="0.3"
                  className="animate-ping"
                />
                
                {/* Main marker */}
                <circle
                  cx={x}
                  cy={y}
                  r="6"
                  fill={getSeverityColor(marker.severity)}
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer hover:r-8 transition-all duration-200"
                />
                
                {/* Type icon */}
                <text
                  x={x}
                  y={y + 2}
                  textAnchor="middle"
                  fontSize="8"
                  className="pointer-events-none"
                >
                  {getTypeIcon(marker.type)}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 border border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Alert Severity</h4>
          <div className="space-y-2">
            {[
              { severity: 'critical', label: 'Critical', color: '#ef4444' },
              { severity: 'warning', label: 'Warning', color: '#f97316' },
              { severity: 'watch', label: 'Watch', color: '#3b82f6' },
              { severity: 'info', label: 'Info', color: '#10b981' }
            ].map(item => (
              <div key={item.severity} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-xs text-gray-600">{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Stats overlay */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 border border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{mapMarkers.length}</div>
            <div className="text-xs text-gray-500">Active Alerts</div>
          </div>
        </div>

        {/* Loading state */}
        {state.isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    </div>
  );
}