import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Alert, DashboardStats, RealTimeStats } from '../api/client';

interface AppState {
  alerts: Alert[];
  dashboardStats: DashboardStats | null;
  realTimeStats: RealTimeStats | null;
  selectedAlert: Alert | null;
  filters: {
    severity: string[];
    timeRange: number;
    location: string;
  };
  isLoading: boolean;
  error: string | null;
  pathwayConnected: boolean;
  lastUpdate: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_ALERTS'; payload: Alert[] }
  | { type: 'SET_DASHBOARD_STATS'; payload: DashboardStats }
  | { type: 'SET_REAL_TIME_STATS'; payload: RealTimeStats }
  | { type: 'SET_SELECTED_ALERT'; payload: Alert | null }
  | { type: 'UPDATE_FILTERS'; payload: Partial<AppState['filters']> }
  | { type: 'ACKNOWLEDGE_ALERT'; payload: number }
  | { type: 'SET_PATHWAY_CONNECTED'; payload: boolean }
  | { type: 'SET_LAST_UPDATE'; payload: string }
  | { type: 'ADD_ALERT'; payload: Alert }
  | { type: 'UPDATE_ALERT'; payload: Alert };

const initialState: AppState = {
  alerts: [],
  dashboardStats: null,
  realTimeStats: null,
  selectedAlert: null,
  filters: {
    severity: [],
    timeRange: 24,
    location: '',
  },
  isLoading: false,
  error: null,
  pathwayConnected: false,
  lastUpdate: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    
    case 'SET_ALERTS':
      return { ...state, alerts: action.payload };
    
    case 'SET_DASHBOARD_STATS':
      return { ...state, dashboardStats: action.payload };
    
    case 'SET_REAL_TIME_STATS':
      return { ...state, realTimeStats: action.payload };
    
    case 'SET_SELECTED_ALERT':
      return { ...state, selectedAlert: action.payload };
    
    case 'UPDATE_FILTERS':
      return { 
        ...state, 
        filters: { ...state.filters, ...action.payload }
      };
    
    case 'ACKNOWLEDGE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload
            ? { ...alert, acknowledged: true }
            : alert
        ),
      };
    
    case 'SET_PATHWAY_CONNECTED':
      return { ...state, pathwayConnected: action.payload };
    
    case 'SET_LAST_UPDATE':
      return { ...state, lastUpdate: action.payload };
    
    case 'ADD_ALERT':
      return {
        ...state,
        alerts: [action.payload, ...state.alerts],
      };
    
    case 'UPDATE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload.id ? action.payload : alert
        ),
      };
    
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
} 