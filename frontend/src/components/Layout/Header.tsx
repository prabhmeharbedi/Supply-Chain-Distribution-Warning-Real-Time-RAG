import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Box,
  IconButton,
  InputBase,
  Badge,
  Avatar,
  Typography,
  Menu,
  MenuItem,
  Divider,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Popover,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  Refresh as RefreshIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Fullscreen as FullscreenIcon,
} from '@mui/icons-material';
import { alpha, styled } from '@mui/material/styles';
import { useAppContext } from '../../contexts/AppContext';
import { format } from 'date-fns';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(1),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  width: '100%',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    [theme.breakpoints.up('sm')]: {
      width: '20ch',
      '&:focus': {
        width: '30ch',
      },
    },
  },
}));

export default function Header() {
  const { state, dispatch } = useAppContext();
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  React.useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const unreadNotifications = state.alerts.filter(
    alert => !alert.acknowledged && alert.severity === 'critical'
  ).length;

  const refreshData = () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    setTimeout(() => {
      dispatch({ type: 'SET_LOADING', payload: false });
    }, 1000);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: 'background.paper',
        color: 'text.primary',
        boxShadow: 1,
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Search */}
        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search alerts, locations, or routes..."
              inputProps={{ 'aria-label': 'search' }}
            />
          </Search>
        </Box>

        {/* Center - Time and Status */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {format(currentTime, 'EEEE, MMMM d')}
          </Typography>
          <Typography variant="body2" fontFamily="monospace" color="text.primary">
            {format(currentTime, 'HH:mm:ss')}
          </Typography>
          <Chip label="UTC" size="small" color="success" variant="outlined" />
        </Box>

        {/* Right side - Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Refresh Button */}
          <IconButton
            onClick={refreshData}
            disabled={state.isLoading}
            color="inherit"
            sx={{
              '& svg': {
                animation: state.isLoading ? 'spin 1s linear infinite' : 'none',
              },
            }}
          >
            <RefreshIcon />
          </IconButton>

          {/* Theme Toggle */}
          <IconButton
            onClick={() => dispatch({ type: 'TOGGLE_THEME' })}
            color="inherit"
          >
            {state.theme === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>

          {/* Notifications */}
          <IconButton
            onClick={handleNotificationsOpen}
            color="inherit"
          >
            <Badge badgeContent={unreadNotifications} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* User Menu */}
          <IconButton
            onClick={handleUserMenuOpen}
            color="inherit"
            sx={{ ml: 1 }}
          >
            {state.user?.avatar ? (
              <Avatar
                src={state.user.avatar}
                alt={state.user.name}
                sx={{ width: 32, height: 32 }}
              />
            ) : (
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                <AccountIcon />
              </Avatar>
            )}
          </IconButton>

          {/* User name (hidden on mobile) */}
          <Box sx={{ display: { xs: 'none', md: 'block' }, ml: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              {state.user?.name || 'Alex Chen'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {state.user?.role || 'Supply Chain Manager'}
            </Typography>
          </Box>
        </Box>
      </Toolbar>

      {/* Notifications Popover */}
      <Popover
        open={Boolean(notificationsAnchor)}
        anchorEl={notificationsAnchor}
        onClose={handleNotificationsClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Paper sx={{ width: 320, maxHeight: 400 }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">Notifications</Typography>
            <Typography variant="body2" color="text.secondary">
              {unreadNotifications} unread
            </Typography>
          </Box>
          <List sx={{ maxHeight: 300, overflow: 'auto' }}>
            {state.alerts
              .filter(alert => !alert.acknowledged && alert.severity === 'critical')
              .slice(0, 5)
              .map(alert => (
                <ListItem key={alert.id} divider>
                  <ListItemIcon>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'error.main',
                      }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.title}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {alert.location}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                          {format(alert.createdAt, 'HH:mm')}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
          </List>
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography
              variant="body2"
              color="primary"
              sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
            >
              View all notifications
            </Typography>
          </Box>
        </Paper>
      </Popover>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ p: 2, minWidth: 200 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            {state.user?.name || 'Alex Chen'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {state.user?.email || 'alex.chen@company.com'}
          </Typography>
        </Box>
        <Divider />
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon>
            <AccountIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon>
            <FullscreenIcon fontSize="small" />
          </ListItemIcon>
          Full Screen
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleUserMenuClose} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" sx={{ color: 'error.main' }} />
          </ListItemIcon>
          Sign Out
        </MenuItem>
      </Menu>
    </AppBar>
  );
}