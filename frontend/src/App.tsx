import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import Dashboard from './components/Dashboard/Dashboard';
import RealTimeDemo from './components/RealTimeDemo/RealTimeDemo';
import PathwayRAG from './components/PathwayRAG/PathwayRAG';
import Navigation from './components/Navigation/Navigation';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Real-Time RAG Supply Chain Dashboard
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Powered by Pathway
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Navigation />
      
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/pathway-rag" element={<PathwayRAG />} />
          <Route path="/real-time-demo" element={<RealTimeDemo />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App; 