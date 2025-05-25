import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Typography,
  Box,
  Divider
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Check as CheckIcon
} from '@mui/icons-material';
import { Alert } from '../../api/client';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

interface AlertsListProps {
  alerts: Alert[];
  onAcknowledge: (id: number) => void;
}

const AlertsList: React.FC<AlertsListProps> = ({ alerts, onAcknowledge }) => {
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

  if (!alerts || alerts.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No alerts in the last 24 hours
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Your supply chain is running smoothly
        </Typography>
      </Box>
    );
  }

  return (
    <List sx={{ maxHeight: 400, overflow: 'auto' }}>
      {alerts.map((alert, index) => (
        <React.Fragment key={alert.id}>
          <ListItem
            sx={{
              opacity: alert.acknowledged ? 0.6 : 1,
              backgroundColor: alert.acknowledged ? 'grey.50' : 'transparent'
            }}
          >
            <ListItemIcon>
              {getSeverityIcon(alert.severity)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {alert.title}
                  </Typography>
                  <Chip
                    label={alert.severity}
                    size="small"
                    color={getSeverityColor(alert.severity)}
                    variant="outlined"
                  />
                  {alert.should_alert && (
                    <Chip
                      label="Action Required"
                      size="small"
                      color="error"
                      variant="filled"
                    />
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {alert.description}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                    {alert.location && (
                      <Typography variant="caption" color="text.secondary">
                        📍 {alert.location}
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary">
                      🕒 {dayjs(alert.created_at).fromNow()}
                    </Typography>
                    {alert.confidence_score && (
                      <Typography variant="caption" color="text.secondary">
                        🎯 {Math.round(alert.confidence_score * 100)}% confidence
                      </Typography>
                    )}
                    {alert.alert_score && (
                      <Typography variant="caption" color="text.secondary">
                        ⚡ Score: {alert.alert_score.toFixed(2)}
                      </Typography>
                    )}
                  </Box>
                </Box>
              }
            />
            <ListItemSecondaryAction>
              {!alert.acknowledged && (
                <IconButton
                  edge="end"
                  aria-label="acknowledge"
                  onClick={() => onAcknowledge(alert.id)}
                  color="primary"
                  size="small"
                >
                  <CheckIcon />
                </IconButton>
              )}
            </ListItemSecondaryAction>
          </ListItem>
          {index < alerts.length - 1 && <Divider />}
        </React.Fragment>
      ))}
    </List>
  );
};

export default AlertsList; 