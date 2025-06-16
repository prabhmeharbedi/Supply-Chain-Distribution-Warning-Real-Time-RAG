import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Badge,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning as AlertIcon,
  Public as MapIcon,
  Analytics as AnalyticsIcon,
  Security as SecurityIcon,
  TrendingUp as PerformanceIcon,
  Notifications as NotificationsIcon,
  Group as TeamIcon,
  Description as ReportsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { useAppContext } from '../../contexts/AppContext';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: DashboardIcon,
    description: 'Overview & key metrics',
    active: true,
  },
  {
    name: 'Alerts',
    href: '/alerts',
    icon: AlertIcon,
    description: 'Active disruptions',
    active: false,
  },
  {
    name: 'Map View',
    href: '/map',
    icon: MapIcon,
    description: 'Geographic visualization',
    active: false,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: AnalyticsIcon,
    description: 'Historical trends',
    active: false,
  },
  {
    name: 'Risk Assessment',
    href: '/risk',
    icon: SecurityIcon,
    description: 'Vulnerability analysis',
    active: false,
  },
  {
    name: 'Performance',
    href: '/performance',
    icon: PerformanceIcon,
    description: 'System metrics',
    active: false,
  },
];

const secondaryItems = [
  {
    name: 'Notifications',
    href: '/notifications',
    icon: NotificationsIcon,
    description: 'Alert preferences',
  },
  {
    name: 'Team',
    href: '/team',
    icon: TeamIcon,
    description: 'User management',
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: ReportsIcon,
    description: 'Export & reporting',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: SettingsIcon,
    description: 'System configuration',
  },
];

export default function Sidebar() {
  const theme = useTheme();
  const { state } = useAppContext();
  const criticalAlertsCount = state.alerts.filter(
    alert => alert.severity === 'critical' && !alert.acknowledged
  ).length;

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        backgroundColor: 'background.paper',
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              backgroundColor: 'primary.main',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2,
            }}
          >
            <SecurityIcon sx={{ color: 'white', fontSize: 24 }} />
          </Box>
          <Box>
            <Typography variant="h6" fontWeight="bold" color="text.primary">
              Supply Chain
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monitor
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              backgroundColor: 'success.main',
              borderRadius: '50%',
              animation: 'pulse 2s infinite',
            }}
          />
          <Typography variant="body2" color="text.secondary">
            Live • Real-time data
          </Typography>
        </Box>
      </Box>

      {/* Main Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ px: 2, py: 1 }}>
          {navigationItems.map((item) => (
            <ListItem key={item.name} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  backgroundColor: item.active ? 'primary.50' : 'transparent',
                  color: item.active ? 'primary.main' : 'text.primary',
                  '&:hover': {
                    backgroundColor: item.active ? 'primary.100' : 'action.hover',
                  },
                  borderRight: item.active ? 3 : 0,
                  borderColor: 'primary.main',
                }}
              >
                <ListItemIcon
                  sx={{
                    color: item.active ? 'primary.main' : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.name === 'Alerts' && criticalAlertsCount > 0 ? (
                    <Badge badgeContent={criticalAlertsCount} color="error">
                      <item.icon />
                    </Badge>
                  ) : (
                    <item.icon />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight={item.active ? 600 : 400}>
                      {item.name}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ mx: 2, my: 2 }} />

        {/* Secondary Navigation */}
        <List sx={{ px: 2 }}>
          {secondaryItems.map((item) => (
            <ListItem key={item.name} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                sx={{
                  borderRadius: 2,
                  py: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  <item.icon />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      {item.name}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Status Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label="System Operational"
            color="success"
            size="small"
            variant="outlined"
          />
          <Chip
            label="95% Uptime"
            color="primary"
            size="small"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
}