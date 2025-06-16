import React from 'react';
import { Box, Toolbar } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';
import Dashboard from '../Dashboard/Dashboard';

const SIDEBAR_WIDTH = 280;

export default function Layout() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar - Fixed position */}
      <Box
        sx={{
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          position: 'fixed',
          left: 0,
          top: 0,
          height: '100vh',
          zIndex: 1200,
        }}
      >
        <Sidebar />
      </Box>

      {/* Main content area */}
      <Box
        sx={{
          flexGrow: 1,
          marginLeft: `${SIDEBAR_WIDTH}px`,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <Header />
        
        {/* Toolbar spacer to push content below the fixed AppBar */}
        <Toolbar />

        {/* Main content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            backgroundColor: '#f5f5f5',
            padding: 2,
          }}
        >
          <Dashboard />
        </Box>
      </Box>
    </Box>
  );
}