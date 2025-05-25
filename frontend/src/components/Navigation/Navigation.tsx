import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Tabs, 
  Tab, 
  Chip,
  useTheme 
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Timeline as TimelineIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { useAppContext } from '../../contexts/AppContext';

const Navigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const { state } = useAppContext();

  const tabs = [
    {
      label: 'Dashboard',
      value: '/dashboard',
      icon: <DashboardIcon />,
      description: 'Supply Chain Overview'
    },
    {
      label: 'Pathway RAG',
      value: '/pathway-rag',
      icon: <PsychologyIcon />,
      description: 'Real-Time RAG Interface'
    },
    {
      label: 'Real-Time Demo',
      value: '/real-time-demo',
      icon: <TimelineIcon />,
      description: 'Live Capability Proof'
    },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    navigate(newValue);
  };

  return (
    <Box sx={{ 
      borderBottom: 1, 
      borderColor: 'divider',
      backgroundColor: 'background.paper',
      px: 2
    }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        maxWidth: 'xl',
        mx: 'auto'
      }}>
        <Tabs
          value={location.pathname}
          onChange={handleTabChange}
          aria-label="navigation tabs"
          sx={{ minHeight: 48 }}
        >
          {tabs.map((tab) => (
            <Tab
              key={tab.value}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {tab.icon}
                  <Box>
                    <Box sx={{ fontWeight: 600 }}>{tab.label}</Box>
                    <Box sx={{ 
                      fontSize: '0.75rem', 
                      opacity: 0.7,
                      fontWeight: 400 
                    }}>
                      {tab.description}
                    </Box>
                  </Box>
                </Box>
              }
              value={tab.value}
              sx={{ 
                textTransform: 'none',
                minHeight: 48,
                py: 1
              }}
            />
          ))}
        </Tabs>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            label={state.pathwayConnected ? 'Pathway Connected' : 'Pathway Disconnected'}
            color={state.pathwayConnected ? 'success' : 'error'}
            size="small"
            variant="outlined"
          />
          {state.lastUpdate && (
            <Chip
              label={`Updated: ${new Date(state.lastUpdate).toLocaleTimeString()}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Navigation; 