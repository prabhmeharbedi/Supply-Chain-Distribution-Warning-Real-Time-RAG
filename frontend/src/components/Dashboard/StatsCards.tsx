import React from 'react';
import { 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box,
  Chip
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  Route as RouteIcon,
  Speed as SpeedIcon,
  HealthAndSafety as HealthIcon
} from '@mui/icons-material';
import { DashboardStats } from '../../api/client';

interface StatsCardsProps {
  stats: DashboardStats | null;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  if (!stats) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={i}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: 1, 
                    backgroundColor: 'grey.100',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <SpeedIcon color="disabled" />
                  </Box>
                  <Box>
                    <Typography variant="h6" color="text.secondary">
                      --
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Loading...
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  const cards = [
    {
      title: 'Total Alerts (24h)',
      value: stats.total_alerts_24h,
      icon: <WarningIcon />,
      color: 'warning' as const,
      bgColor: 'warning.light'
    },
    {
      title: 'Critical Alerts',
      value: stats.critical_alerts_24h,
      icon: <ErrorIcon />,
      color: 'error' as const,
      bgColor: 'error.light'
    },
    {
      title: 'Active Disruptions',
      value: stats.active_disruptions,
      icon: <TrendingUpIcon />,
      color: 'info' as const,
      bgColor: 'info.light'
    },
    {
      title: 'Affected Routes',
      value: stats.affected_routes?.length || 0,
      icon: <RouteIcon />,
      color: 'secondary' as const,
      bgColor: 'secondary.light'
    },
    {
      title: 'Avg Confidence',
      value: `${Math.round((stats.average_confidence || 0) * 100)}%`,
      icon: <SpeedIcon />,
      color: 'success' as const,
      bgColor: 'success.light'
    },
    {
      title: 'System Health',
      value: stats.system_health,
      icon: <HealthIcon />,
      color: stats.system_health === 'healthy' ? 'success' as const : 'warning' as const,
      bgColor: stats.system_health === 'healthy' ? 'success.light' : 'warning.light'
    }
  ];

  return (
    <Grid container spacing={3}>
      {cards.map((card, index) => (
        <Grid item xs={12} sm={6} md={4} lg={2} key={index}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  p: 1, 
                  borderRadius: 1, 
                  backgroundColor: card.bgColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white'
                }}>
                  {card.icon}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5" component="div" fontWeight="bold">
                    {card.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.title}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StatsCards; 