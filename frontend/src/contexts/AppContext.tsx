import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Alert, DashboardStats, User } from '../types';
import { mockDataService } from '../services/mockDataService';

interface AppState {
  alerts: Alert[];
  dashboardStats: DashboardStats;
  selectedAlert: Alert | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: boolean;
  lastUpdate: Date | null;
}

type AppAction =
  | { type: 'SET_ALERTS'; payload: Alert[] }
  | { type: 'SET_DASHBOARD_STATS'; payload: DashboardStats }
  | { type: 'SET_SELECTED_ALERT'; payload: Alert | null }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_SIDEBAR'; payload: boolean }
  | { type: 'TOGGLE_THEME' }
  | { type: 'ACKNOWLEDGE_ALERT'; payload: string }
  | { type: 'TOGGLE_NOTIFICATIONS' }
  | { type: 'SET_LAST_UPDATE'; payload: Date };

const initialState: AppState = {
  alerts: [],
  dashboardStats: {
    totalAlerts24h: 0,
    criticalAlerts: 0,
    activeDisruptions: 0,
    systemHealth: 'operational',
    averageConfidence: 0,
    topAffectedRoutes: [],
  },
  selectedAlert: null,
  user: {
    id: '1',
    name: 'Alex Chen',
    email: 'alex.chen@company.com',
    role: 'Supply Chain Manager',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
  },
  isLoading: false,
  error: null,
  sidebarOpen: true,
  theme: 'light',
  notifications: true,
  lastUpdate: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_ALERTS':
      return { ...state, alerts: action.payload };
    case 'SET_DASHBOARD_STATS':
      return { ...state, dashboardStats: action.payload };
    case 'SET_SELECTED_ALERT':
      return { ...state, selectedAlert: action.payload };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };
    case 'SET_SIDEBAR':
      return { ...state, sidebarOpen: action.payload };
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' };
    case 'ACKNOWLEDGE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload ? { ...alert, acknowledged: true } : alert
        ),
      };
    case 'TOGGLE_NOTIFICATIONS':
      return { ...state, notifications: !state.notifications };
    case 'SET_LAST_UPDATE':
      return { ...state, lastUpdate: action.payload };
    default:
      return state;
  }
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  acknowledgeAlert: (id: string) => void;
} | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const acknowledgeAlert = (id: string) => {
    mockDataService.acknowledgeAlert(id);
    dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: id });
  };

  useEffect(() => {
    // Load initial data
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const alerts = mockDataService.getAlerts();
      const stats = mockDataService.getDashboardStats();
      
      dispatch({ type: 'SET_ALERTS', payload: alerts });
      dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
      dispatch({ type: 'SET_LAST_UPDATE', payload: new Date() });
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load initial data' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }

    // Subscribe to real-time updates
    const unsubscribe = mockDataService.subscribeToUpdates((alerts) => {
      dispatch({ type: 'SET_ALERTS', payload: alerts });
      dispatch({ type: 'SET_LAST_UPDATE', payload: new Date() });
      
      // Update dashboard stats
      const stats = mockDataService.getDashboardStats();
      dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
    });

    // Update stats periodically
    const statsInterval = setInterval(() => {
      const stats = mockDataService.getDashboardStats();
      dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
    }, 30000);

    return () => {
      unsubscribe();
      clearInterval(statsInterval);
    };
  }, []);

  return (
    <AppContext.Provider value={{ state, dispatch, acknowledgeAlert }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}