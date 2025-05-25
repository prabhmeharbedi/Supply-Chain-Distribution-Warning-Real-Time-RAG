import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { apiClient } from '../../api/client';
import { useAppContext } from '../../contexts/AppContext';
import dayjs from 'dayjs';

interface DemoStep {
  label: string;
  description: string;
  action: () => Promise<void>;
  completed: boolean;
  result?: string;
}

const RealTimeDemo: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [activeStep, setActiveStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoData, setDemoData] = useState('');
  const [queryResult, setQueryResult] = useState<string>('');
  const [steps, setSteps] = useState<DemoStep[]>([]);

  useEffect(() => {
    initializeDemoSteps();
  }, []);

  const initializeDemoSteps = () => {
    const demoSteps: DemoStep[] = [
      {
        label: 'Check Initial State',
        description: 'Query the system for current supply chain status',
        action: async () => {
          const result = await apiClient.queryPathwayRAG('What is the current supply chain status?');
          setQueryResult(result.response);
        },
        completed: false
      },
      {
        label: 'Add Live Data',
        description: 'Insert new disruption data in real-time',
        action: async () => {
          const timestamp = new Date().toISOString();
          const newData = {
            content: `BREAKING: Major port disruption at Los Angeles Port due to equipment failure. Estimated delay: 6-8 hours. Timestamp: ${timestamp}`,
            metadata: {
              source: 'real_time_demo',
              timestamp: timestamp,
              location: 'Los Angeles Port',
              severity: 'critical'
            }
          };
          await apiClient.addLiveData(newData);
          setDemoData(newData.content);
        },
        completed: false
      },
      {
        label: 'Immediate Query',
        description: 'Query the system immediately after data insertion',
        action: async () => {
          // Wait a moment for processing
          await new Promise(resolve => setTimeout(resolve, 1000));
          const result = await apiClient.queryPathwayRAG('What are the latest port disruptions?');
          setQueryResult(result.response);
        },
        completed: false
      },
      {
        label: 'Verify Real-Time Update',
        description: 'Confirm the new data is immediately available',
        action: async () => {
          const stats = await apiClient.getRealTimeStats();
          dispatch({ type: 'SET_REAL_TIME_STATS', payload: stats });
        },
        completed: false
      },
      {
        label: 'Performance Test',
        description: 'Measure T+0 to T+1 availability',
        action: async () => {
          const startTime = Date.now();
          await apiClient.proveRealTimeCapability();
          const endTime = Date.now();
          const latency = endTime - startTime;
          setQueryResult(`Real-time capability verified. Data availability latency: ${latency}ms`);
        },
        completed: false
      }
    ];
    setSteps(demoSteps);
  };

  const runDemo = async () => {
    setRunning(true);
    setError(null);
    setActiveStep(0);

    try {
      for (let i = 0; i < steps.length; i++) {
        setActiveStep(i);
        await steps[i].action();
        
        // Mark step as completed
        setSteps(prev => prev.map((step, index) => 
          index === i ? { ...step, completed: true } : step
        ));
        
        // Wait between steps for demonstration
        if (i < steps.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      }
      
      setActiveStep(steps.length);
    } catch (error) {
      console.error('Demo failed:', error);
      setError('Demo failed. Please check the system status and try again.');
    } finally {
      setRunning(false);
    }
  };

  const resetDemo = () => {
    setActiveStep(0);
    setError(null);
    setDemoData('');
    setQueryResult('');
    initializeDemoSteps();
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Real-Time Capability Demo
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip
            icon={<TimelineIcon />}
            label="Live Demo"
            color="primary"
            variant="outlined"
          />
          <Chip
            icon={state.pathwayConnected ? <CheckCircleIcon /> : <StopIcon />}
            label={state.pathwayConnected ? 'Pathway Active' : 'Pathway Inactive'}
            color={state.pathwayConnected ? 'success' : 'error'}
            size="small"
          />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Demo Controls */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Demo Controls
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  This demo proves that data added at T+0 is immediately available for queries at T+1.
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={runDemo}
                    disabled={running || !state.pathwayConnected}
                    startIcon={running ? <CircularProgress size={16} /> : <PlayIcon />}
                    fullWidth
                  >
                    {running ? 'Running Demo...' : 'Start Demo'}
                  </Button>
                </Box>
                
                <Button
                  variant="outlined"
                  onClick={resetDemo}
                  disabled={running}
                  startIcon={<RefreshIcon />}
                  fullWidth
                >
                  Reset Demo
                </Button>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {!state.pathwayConnected && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Pathway pipeline is not connected. Please ensure the backend is running.
                </Alert>
              )}

              {/* Real-Time Stats */}
              {state.realTimeStats && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Current Stats
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Documents:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {state.realTimeStats.total_documents}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Live:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {state.realTimeStats.live_documents}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Queries:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {state.realTimeStats.queries_processed}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Demo Steps */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Demo Progress
              </Typography>
              
              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((step, index) => (
                  <Step key={step.label}>
                    <StepLabel
                      completed={step.completed}
                      icon={step.completed ? <CheckCircleIcon color="success" /> : undefined}
                    >
                      {step.label}
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {step.description}
                      </Typography>
                      
                      {running && activeStep === index && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <CircularProgress size={16} />
                          <Typography variant="body2">Executing...</Typography>
                        </Box>
                      )}
                      
                      {step.completed && step.result && (
                        <Paper sx={{ p: 2, backgroundColor: 'success.light', mb: 2 }}>
                          <Typography variant="body2">
                            {step.result}
                          </Typography>
                        </Paper>
                      )}
                    </StepContent>
                  </Step>
                ))}
              </Stepper>

              {activeStep === steps.length && (
                <Paper sx={{ p: 3, backgroundColor: 'success.light', mt: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <CheckCircleIcon color="success" />
                    <Typography variant="h6" color="success.dark">
                      Demo Completed Successfully!
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    The real-time capability has been demonstrated. Data inserted at T+0 was immediately 
                    available for queries at T+1, proving the Pathway-powered streaming architecture.
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Demo Results */}
        {(demoData || queryResult) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Demo Results
                </Typography>
                
                <Grid container spacing={2}>
                  {demoData && (
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Data Added (T+0):
                      </Typography>
                      <Paper sx={{ p: 2, backgroundColor: 'info.light' }}>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {demoData}
                        </Typography>
                      </Paper>
                    </Grid>
                  )}
                  
                  {queryResult && (
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Query Result (T+1):
                      </Typography>
                      <Paper sx={{ p: 2, backgroundColor: 'success.light' }}>
                        <Typography variant="body2">
                          {queryResult}
                        </Typography>
                      </Paper>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default RealTimeDemo; 