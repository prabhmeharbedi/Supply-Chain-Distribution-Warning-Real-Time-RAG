import React, { useEffect, useState } from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  CircularProgress, 
  Alert,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { 
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useAppContext } from '../../contexts/AppContext';
import { apiClient } from '../../api/client';
import StatsCards from './StatsCards';
import AlertsList from './AlertsList';
import SystemHealth from './SystemHealth';

const Dashboard: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1);
    }, 30000);
    
    return () => clearInterval(interval);
  }, [refreshKey]);

  const loadDashboardData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Load dashboard stats
      const stats = await apiClient.getDashboardStats();
      dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
      
      // Load recent alerts
      const alertsResponse = await apiClient.getAlerts({
        page: 1,
        page_size: 20,
        hours_back: 24
      });
      dispatch({ type: 'SET_ALERTS', payload: alertsResponse.alerts || [] });
      
      // Check Pathway connection
      try {
        await apiClient.getPathwayHealth();
        dispatch({ type: 'SET_PATHWAY_CONNECTED', payload: true });
      } catch (error) {
        dispatch({ type: 'SET_PATHWAY_CONNECTED', payload: false });
      }
      
      dispatch({ type: 'SET_LAST_UPDATE', payload: new Date().toISOString() });
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load dashboard data' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <CheckCircleIcon color="success" />;
    }
  };

  const getSeverityColor = (severity: string): "error" | "warning" | "info" | "success" => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'success';
    }
  };

  if (state.isLoading && !state.dashboardStats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (state.error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {state.error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Supply Chain Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip
            icon={state.pathwayConnected ? <CheckCircleIcon /> : <ErrorIcon />}
            label={state.pathwayConnected ? 'Real-Time Active' : 'Real-Time Inactive'}
            color={state.pathwayConnected ? 'success' : 'error'}
            variant="outlined"
          />
          {state.isLoading && <CircularProgress size={20} />}
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12}>
          <StatsCards stats={state.dashboardStats} />
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={4}>
          <SystemHealth />
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Alerts (24h)
              </Typography>
              <AlertsList 
                alerts={state.alerts.slice(0, 10)} 
                onAcknowledge={(id) => {
                  dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: id });
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Alert Summary by Severity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alert Distribution
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {['critical', 'warning', 'info'].map((severity) => {
                  const count = state.alerts.filter(alert => alert.severity === severity).length;
                  return (
                    <Box key={severity} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {getSeverityIcon(severity)}
                      <Typography sx={{ textTransform: 'capitalize', minWidth: 80 }}>
                        {severity}
                      </Typography>
                      <Chip 
                        label={count} 
                        color={getSeverityColor(severity)}
                        size="small"
                      />
                    </Box>
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography>Pathway Pipeline</Typography>
                  <Chip 
                    label={state.pathwayConnected ? 'Active' : 'Inactive'}
                    color={state.pathwayConnected ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography>Data Sources</Typography>
                  <Chip 
                    label="Connected"
                    color="success"
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography>AI Analysis</Typography>
                  <Chip 
                    label="Operational"
                    color="success"
                    size="small"
                  />
                </Box>
                {state.lastUpdate && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography>Last Update</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(state.lastUpdate).toLocaleTimeString()}
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 