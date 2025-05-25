import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
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
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Send as SendIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { apiClient, PathwayRAGResponse, RealTimeStats } from '../../api/client';
import { useAppContext } from '../../contexts/AppContext';
import dayjs from 'dayjs';

const PathwayRAG: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<PathwayRAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [realTimeStats, setRealTimeStats] = useState<RealTimeStats | null>(null);
  const [queryHistory, setQueryHistory] = useState<PathwayRAGResponse[]>([]);

  useEffect(() => {
    loadRealTimeStats();
    const interval = setInterval(loadRealTimeStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadRealTimeStats = async () => {
    try {
      const stats = await apiClient.getRealTimeStats();
      setRealTimeStats(stats);
      dispatch({ type: 'SET_REAL_TIME_STATS', payload: stats });
    } catch (error) {
      console.error('Failed to load real-time stats:', error);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.queryPathwayRAG(query);
      setResponse(result);
      setQueryHistory(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 queries
      setQuery('');
    } catch (error) {
      console.error('Query failed:', error);
      setError('Failed to process query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleQuery();
    }
  };

  const sampleQueries = [
    "What are the current supply chain disruptions?",
    "Show me recent weather alerts affecting logistics",
    "What ports are experiencing delays?",
    "Are there any earthquake impacts on shipping routes?",
    "What's the status of major transportation hubs?",
    "Show me critical alerts from the last hour"
  ];

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Pathway RAG Interface
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip
            icon={<PsychologyIcon />}
            label="Real-Time RAG"
            color="primary"
            variant="outlined"
          />
          <IconButton onClick={loadRealTimeStats} size="small">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Real-Time Stats */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real-Time System Status
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <StorageIcon sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h5" fontWeight="bold">
                      {realTimeStats?.total_documents || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Documents
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <AccessTimeIcon sx={{ fontSize: 32, color: 'success.main', mb: 1 }} />
                    <Typography variant="h5" fontWeight="bold">
                      {realTimeStats?.live_documents || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Live Documents
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <SpeedIcon sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                    <Typography variant="h5" fontWeight="bold">
                      {realTimeStats?.queries_processed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Queries Processed
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <PsychologyIcon sx={{ fontSize: 32, color: 'info.main', mb: 1 }} />
                    <Typography variant="h5" fontWeight="bold">
                      {realTimeStats?.average_response_time ? `${realTimeStats.average_response_time.toFixed(0)}ms` : '--'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Response Time
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              {realTimeStats?.last_update && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {dayjs(realTimeStats.last_update).format('YYYY-MM-DD HH:mm:ss')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Query Interface */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ask About Supply Chain Status
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about supply chain disruptions, weather impacts, port status, etc..."
                  variant="outlined"
                  disabled={loading}
                />
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    Press Enter to send, Shift+Enter for new line
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={handleQuery}
                    disabled={loading || !query.trim()}
                    startIcon={loading ? <CircularProgress size={16} /> : <SendIcon />}
                  >
                    {loading ? 'Processing...' : 'Send Query'}
                  </Button>
                </Box>
              </Box>

              {/* Sample Queries */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Sample Queries:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {sampleQueries.map((sample, index) => (
                    <Chip
                      key={index}
                      label={sample}
                      variant="outlined"
                      size="small"
                      onClick={() => setQuery(sample)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {/* Current Response */}
              {response && (
                <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Query: {response.query}
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
                    {response.response}
                  </Typography>
                  
                  {response.sources && response.sources.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle2">
                          Sources ({response.sources.length})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {response.sources.map((source, index) => (
                            <ListItem key={index} sx={{ px: 0 }}>
                              <ListItemText
                                primary={source.content.substring(0, 200) + '...'}
                                secondary={
                                  <Box>
                                    <Typography variant="caption">
                                      Score: {source.score.toFixed(3)}
                                    </Typography>
                                    {source.metadata && Object.keys(source.metadata).length > 0 && (
                                      <Typography variant="caption" sx={{ ml: 2 }}>
                                        {Object.entries(source.metadata).map(([key, value]) => 
                                          `${key}: ${value}`
                                        ).join(', ')}
                                      </Typography>
                                    )}
                                  </Box>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                  
                  <Typography variant="caption" color="text.secondary">
                    Processing time: {response.processing_time}ms | {dayjs(response.timestamp).format('HH:mm:ss')}
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Query History */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Queries
              </Typography>
              
              {queryHistory.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  No queries yet. Try asking about supply chain status!
                </Typography>
              ) : (
                <List dense sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {queryHistory.map((item, index) => (
                    <React.Fragment key={index}>
                      <ListItem sx={{ px: 0, cursor: 'pointer' }} onClick={() => setQuery(item.query)}>
                        <ListItemText
                          primary={item.query}
                          secondary={
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                {dayjs(item.timestamp).format('HH:mm:ss')} | {item.processing_time}ms
                              </Typography>
                              <Typography variant="body2" sx={{ mt: 0.5 }}>
                                {item.response.substring(0, 100)}...
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < queryHistory.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PathwayRAG; 