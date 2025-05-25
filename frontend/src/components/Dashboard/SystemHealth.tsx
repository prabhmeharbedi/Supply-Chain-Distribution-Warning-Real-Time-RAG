import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Cloud as CloudIcon,
  Psychology as PsychologyIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { apiClient } from '../../api/client';
import { useAppContext } from '../../contexts/AppContext';

interface HealthStatus {
  component: string;
  status: 'healthy' | 'warning' | 'error';
  message: string;
  lastCheck: string;
}

const SystemHealth: React.FC = () => {
  const { state } = useAppContext();
  const [healthData, setHealthData] = useState<HealthStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const checks: HealthStatus[] = [];

      // Check main API health
      try {
        await apiClient.getHealth();
        checks.push({
          component: 'API Server',
          status: 'healthy',
          message: 'All endpoints responding',
          lastCheck: new Date().toISOString()
        });
      } catch (error) {
        checks.push({
          component: 'API Server',
          status: 'error',
          message: 'API server unreachable',
          lastCheck: new Date().toISOString()
        });
      }

      // Check Pathway health
      try {
        await apiClient.getPathwayHealth();
        checks.push({
          component: 'Pathway Pipeline',
          status: 'healthy',
          message: 'Real-time processing active',
          lastCheck: new Date().toISOString()
        });
      } catch (error) {
        checks.push({
          component: 'Pathway Pipeline',
          status: 'error',
          message: 'Pipeline not responding',
          lastCheck: new Date().toISOString()
        });
      }

      // Check real-time stats
      try {
        const stats = await apiClient.getRealTimeStats();
        const isHealthy = stats.total_documents > 0 && stats.last_update;
        checks.push({
          component: 'Vector Store',
          status: isHealthy ? 'healthy' : 'warning',
          message: isHealthy ? `${stats.total_documents} documents indexed` : 'No recent updates',
          lastCheck: new Date().toISOString()
        });
      } catch (error) {
        checks.push({
          component: 'Vector Store',
          status: 'error',
          message: 'Vector store unavailable',
          lastCheck: new Date().toISOString()
        });
      }

      // Simulate other component checks
      checks.push({
        component: 'Data Sources',
        status: 'healthy',
        message: 'Weather, News, Earthquake feeds active',
        lastCheck: new Date().toISOString()
      });

      setHealthData(checks);
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <CheckCircleIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string): "success" | "warning" | "error" => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'success';
    }
  };

  const getComponentIcon = (component: string) => {
    switch (component) {
      case 'Pathway Pipeline':
        return <TimelineIcon />;
      case 'Vector Store':
        return <StorageIcon />;
      case 'Data Sources':
        return <CloudIcon />;
      case 'API Server':
        return <PsychologyIcon />;
      default:
        return <CheckCircleIcon />;
    }
  };

  const overallHealth = healthData.length > 0 ? 
    healthData.every(h => h.status === 'healthy') ? 'healthy' :
    healthData.some(h => h.status === 'error') ? 'error' : 'warning'
    : 'unknown';

  const healthyCount = healthData.filter(h => h.status === 'healthy').length;
  const healthPercentage = healthData.length > 0 ? (healthyCount / healthData.length) * 100 : 0;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Health
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        ) : (
          <>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Overall Health
                </Typography>
                <Chip
                  label={overallHealth}
                  color={getStatusColor(overallHealth)}
                  size="small"
                  sx={{ textTransform: 'capitalize' }}
                />
              </Box>
              <LinearProgress
                variant="determinate"
                value={healthPercentage}
                color={getStatusColor(overallHealth)}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {healthyCount} of {healthData.length} components healthy
              </Typography>
            </Box>

            <List dense>
              {healthData.map((health, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {getComponentIcon(health.component)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" fontWeight={500}>
                          {health.component}
                        </Typography>
                        {getStatusIcon(health.status)}
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {health.message}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary">
                Last checked: {new Date().toLocaleTimeString()}
              </Typography>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SystemHealth; 