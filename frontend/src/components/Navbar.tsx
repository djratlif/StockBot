import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as PortfolioIcon,
  TrendingUp as TradingIcon,
  Settings as SettingsIcon,
  BugReport as DebugIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import TimeTicker from './TimeTicker';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { label: 'Portfolio', path: '/portfolio', icon: <PortfolioIcon /> },
    { label: 'Trading', path: '/trading', icon: <TradingIcon /> },
    { label: 'Config', path: '/config', icon: <SettingsIcon /> },
    { label: 'Debug', path: '/debug', icon: <DebugIcon /> },
  ];

  return (
    <AppBar position="static" sx={{ mb: 2 }}>
      <Toolbar sx={{ minHeight: '64px !important' }}>
        <Typography variant="h6" component="div" sx={{ mr: 3 }}>
          StockBot
        </Typography>
        
        {/* Navigation Items */}
        <Box sx={{ display: 'flex', gap: 1, mr: 3 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
        
        {/* Time and Market Status - Right aligned */}
        <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <TimeTicker />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;