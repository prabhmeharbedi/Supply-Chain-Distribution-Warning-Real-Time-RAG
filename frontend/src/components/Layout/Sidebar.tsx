import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  BarChart3,
  Settings,
  Globe,
  TrendingUp,
  Shield,
  Bell,
  Users,
  FileText,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { useAppContext } from '../../contexts/AppContext';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    description: 'Overview & key metrics',
    active: true,
  },
  {
    name: 'Alerts',
    href: '/alerts',
    icon: AlertTriangle,
    description: 'Active disruptions',
    active: false,
  },
  {
    name: 'Map View',
    href: '/map',
    icon: Globe,
    description: 'Geographic visualization',
    active: false,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    description: 'Historical trends',
    active: false,
  },
  {
    name: 'Risk Assessment',
    href: '/risk',
    icon: Shield,
    description: 'Vulnerability analysis',
    active: false,
  },
  {
    name: 'Performance',
    href: '/performance',
    icon: TrendingUp,
    description: 'System metrics',
    active: false,
  },
];

const secondaryItems = [
  {
    name: 'Notifications',
    href: '/notifications',
    icon: Bell,
    description: 'Alert preferences',
  },
  {
    name: 'Team',
    href: '/team',
    icon: Users,
    description: 'User management',
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Export & reporting',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration',
  },
];

export default function Sidebar() {
  const { state } = useAppContext();
  const criticalAlertsCount = state.alerts.filter(
    alert => alert.severity === 'critical' && !alert.acknowledged
  ).length;

  if (!state.sidebarOpen) {
    return (
      <motion.div
        initial={{ width: 280 }}
        animate={{ width: 80 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 h-full bg-white border-r border-neutral-200 z-30 shadow-soft"
      >
        <div className="p-4">
          <div className="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
        </div>
        
        <nav className="mt-8">
          {navigationItems.map((item) => (
            <button
              key={item.name}
              className={clsx(
                'flex items-center px-4 py-3 mx-2 rounded-lg transition-all duration-200 w-full',
                'hover:bg-neutral-100 group relative',
                item.active
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                  : 'text-neutral-600 hover:text-neutral-900'
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name === 'Alerts' && criticalAlertsCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-error-500 text-white text-xs rounded-full flex items-center justify-center">
                  {criticalAlertsCount}
                </span>
              )}
            </button>
          ))}
        </nav>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ width: 80 }}
      animate={{ width: 280 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-full bg-white border-r border-neutral-200 z-30 shadow-soft"
    >
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-neutral-900">Supply Chain</h1>
            <p className="text-sm text-neutral-500">Monitor</p>
          </div>
        </div>
        
        <div className="mt-6 flex items-center space-x-2 text-sm">
          <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse-slow"></div>
          <span className="text-neutral-600">Live</span>
          <span className="text-neutral-400">•</span>
          <span className="text-neutral-500">Real-time data</span>
        </div>
      </div>

      <nav className="mt-8 px-4">
        <div className="space-y-1">
          {navigationItems.map((item) => (
            <button
              key={item.name}
              className={clsx(
                'flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-200 w-full text-left',
                'hover:bg-neutral-100 group relative',
                item.active
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                  : 'text-neutral-600 hover:text-neutral-900'
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.name}</span>
                  {item.name === 'Alerts' && criticalAlertsCount > 0 && (
                    <span className="w-6 h-6 bg-error-500 text-white text-xs rounded-full flex items-center justify-center">
                      {criticalAlertsCount}
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500 mt-0.5">{item.description}</p>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-8 pt-6 border-t border-neutral-200">
          <div className="space-y-1">
            {secondaryItems.map((item) => (
              <button
                key={item.name}
                className={clsx(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 w-full text-left',
                  'hover:bg-neutral-100 group',
                  'text-neutral-600 hover:text-neutral-900'
                )}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                <div className="flex-1">
                  <span className="text-sm font-medium">{item.name}</span>
                  <p className="text-xs text-neutral-500 mt-0.5">{item.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </nav>
    </motion.div>
  );
}