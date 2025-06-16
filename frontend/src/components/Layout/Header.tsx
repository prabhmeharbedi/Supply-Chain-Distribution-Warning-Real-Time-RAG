import React, { useState } from 'react';
import {
  Menu,
  Search,
  Bell,
  Settings,
  User,
  LogOut,
  Sun,
  Moon,
  Maximize,
  RefreshCw,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../../contexts/AppContext';
import { format } from 'date-fns';

export default function Header() {
  const { state, dispatch } = useAppContext();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  React.useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const unreadNotifications = state.alerts.filter(
    alert => !alert.acknowledged && alert.severity === 'critical'
  ).length;

  const refreshData = () => {
    // Trigger data refresh
    dispatch({ type: 'SET_LOADING', payload: true });
    setTimeout(() => {
      dispatch({ type: 'SET_LOADING', payload: false });
    }, 1000);
  };

  return (
    <header className="fixed top-0 right-0 left-0 lg:left-80 bg-white border-b border-neutral-200 z-20 shadow-soft">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
            className="p-2 hover:bg-neutral-100 rounded-lg transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="hidden lg:flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                type="text"
                placeholder="Search alerts, locations, or routes..."
                className="pl-10 pr-4 py-2 w-80 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-4 text-sm text-neutral-600">
            <span>{format(currentTime, 'EEEE, MMMM d')}</span>
            <span className="font-mono">{format(currentTime, 'HH:mm:ss')}</span>
            <span className="text-xs px-2 py-1 bg-success-100 text-success-700 rounded-full">UTC</span>
          </div>

          <button
            onClick={refreshData}
            disabled={state.isLoading}
            className="p-2 hover:bg-neutral-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${state.isLoading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={() => dispatch({ type: 'TOGGLE_THEME' })}
            className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
          >
            {state.theme === 'light' ? (
              <Moon className="w-4 h-4" />
            ) : (
              <Sun className="w-4 h-4" />
            )}
          </button>

          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <Bell className="w-4 h-4" />
              {unreadNotifications > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-error-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadNotifications}
                </span>
              )}
            </button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-strong border border-neutral-200 z-50"
                >
                  <div className="p-4 border-b border-neutral-200">
                    <h3 className="font-semibold text-neutral-900">Notifications</h3>
                    <p className="text-sm text-neutral-500">{unreadNotifications} unread</p>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {state.alerts
                      .filter(alert => !alert.acknowledged && alert.severity === 'critical')
                      .slice(0, 5)
                      .map(alert => (
                        <div key={alert.id} className="p-4 border-b border-neutral-100 hover:bg-neutral-50">
                          <div className="flex items-start space-x-3">
                            <div className="w-2 h-2 bg-error-500 rounded-full mt-2 flex-shrink-0"></div>
                            <div className="flex-1">
                              <p className="text-sm font-medium text-neutral-900">{alert.title}</p>
                              <p className="text-xs text-neutral-500 mt-1">{alert.location}</p>
                              <p className="text-xs text-neutral-400 mt-1">
                                {format(alert.createdAt, 'HH:mm')}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                  <div className="p-4 border-t border-neutral-200">
                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                      View all notifications
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              {state.user?.avatar ? (
                <img
                  src={state.user.avatar}
                  alt={state.user.name}
                  className="w-8 h-8 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-neutral-900">{state.user?.name}</p>
                <p className="text-xs text-neutral-500">{state.user?.role}</p>
              </div>
            </button>

            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-strong border border-neutral-200 z-50"
                >
                  <div className="p-4 border-b border-neutral-200">
                    <p className="font-medium text-neutral-900">{state.user?.name}</p>
                    <p className="text-sm text-neutral-500">{state.user?.email}</p>
                  </div>
                  <div className="py-2">
                    <button className="flex items-center space-x-2 w-full px-4 py-2 text-sm hover:bg-neutral-100 transition-colors">
                      <User className="w-4 h-4" />
                      <span>Profile</span>
                    </button>
                    <button className="flex items-center space-x-2 w-full px-4 py-2 text-sm hover:bg-neutral-100 transition-colors">
                      <Settings className="w-4 h-4" />
                      <span>Settings</span>
                    </button>
                    <button className="flex items-center space-x-2 w-full px-4 py-2 text-sm hover:bg-neutral-100 transition-colors">
                      <Maximize className="w-4 h-4" />
                      <span>Full Screen</span>
                    </button>
                    <hr className="my-2" />
                    <button className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-error-600 hover:bg-error-50 transition-colors">
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}