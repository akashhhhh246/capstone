import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  LayoutDashboard,
  Radio,
  FileSearch,
  GitBranch,
  Share2,
  ShieldAlert,
  PlayCircle,
  Cpu,
  Menu,
} from 'lucide-react';
import { wsService } from '../services/websocket';

const drawerWidth = 260;

const menuItems = [
  { text: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
  { text: 'Live Data Ingestion', path: '/live-data', icon: <Radio size={20} /> },
  { text: 'Content Analysis', path: '/analysis', icon: <FileSearch size={20} /> },
  { text: 'Provenance Explorer', path: '/provenance', icon: <GitBranch size={20} /> },
  { text: 'Propagation Analysis', path: '/propagation', icon: <Share2 size={20} /> },
  { text: 'Campaign Analysis', path: '/campaigns', icon: <ShieldAlert size={20} /> },
  { text: 'Real-Time Simulation', path: '/simulation', icon: <PlayCircle size={20} /> },
  { text: 'Model Governance', path: '/models', icon: <Cpu size={20} /> },
];

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    wsService.connect('global');
    const unsub = wsService.onStatusChange((status) => {
      setWsConnected(status);
    });
    return () => unsub();
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#0D1322' }}>
      {/* Brand Header */}
      <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 38,
            height: 38,
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px rgba(59, 130, 246, 0.5)',
          }}
        >
          <ShieldAlert size={22} color="#FFF" />
        </Box>
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB', lineHeight: 1.1 }}>
            AISHIELD
          </Typography>
          <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 600, fontSize: '0.68rem', letterSpacing: '0.08em' }}>
            LLM INFOOPS PROTOCOL
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.08)' }} />

      {/* Navigation Links */}
      <List sx={{ px: 1.5, py: 2, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const isLiveData = item.path === '/live-data';
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.8 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '8px',
                  py: 1,
                  px: 1.5,
                  backgroundColor: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                  border: isActive ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid transparent',
                  color: isActive ? '#60A5FA' : '#9CA3AF',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.04)',
                    color: '#F3F4F6',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 36,
                    color: isActive ? '#60A5FA' : (isLiveData ? '#34D399' : '#9CA3AF'),
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>{item.text}</span>
                      {isLiveData && (
                        <Chip
                          label="LIVE"
                          size="small"
                          sx={{ height: 16, fontSize: '0.58rem', fontWeight: 800, bgcolor: 'rgba(16, 185, 129, 0.2)', color: '#34D399' }}
                        />
                      )}
                    </Box>
                  }
                  primaryTypographyProps={{
                    fontSize: '0.88rem',
                    fontWeight: isActive ? 700 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.08)' }} />

      {/* Telemetry Status Footer */}
      <Box sx={{ p: 2, backgroundColor: '#090D16' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 600 }}>
            DEFENSE TELEMETRY
          </Typography>
          <Chip
            size="small"
            icon={<Radio size={12} color={wsConnected ? '#10B981' : '#EF4444'} />}
            label={wsConnected ? 'LIVE FEED' : 'OFFLINE'}
            sx={{
              height: 20,
              fontSize: '0.65rem',
              fontWeight: 700,
              bgcolor: wsConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: wsConnected ? '#34D399' : '#F87171',
              border: `1px solid ${wsConnected ? '#10B981' : '#EF4444'}`,
            }}
          />
        </Box>
        <Typography variant="caption" sx={{ color: '#4B5563', display: 'block', mt: 0.5, fontSize: '0.7rem' }}>
          Research Prototype v1.0.0 (Synthetic + Real Feed)
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0B0F19' }}>
      {/* Top AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backgroundColor: 'rgba(11, 15, 25, 0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: 'none',
        }}
      >
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <Menu size={20} />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700, color: '#F9FAFB', fontSize: '1.05rem' }}>
              Information Integrity & AI Defense Workbench
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Chip
              label="OPEN INTELLIGENCE INGESTION"
              size="small"
              sx={{
                bgcolor: 'rgba(59, 130, 246, 0.15)',
                color: '#60A5FA',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                fontWeight: 700,
                fontSize: '0.72rem',
              }}
            />
            <Chip
              label="ETHICS COMPLIANT"
              size="small"
              sx={{
                bgcolor: 'rgba(16, 185, 129, 0.15)',
                color: '#34D399',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontWeight: 700,
                fontSize: '0.72rem',
              }}
            />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, borderRight: '1px solid rgba(255,255,255,0.08)' },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, borderRight: '1px solid rgba(255,255,255,0.08)' },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px',
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: '#0B0F19',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};
