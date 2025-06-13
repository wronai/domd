import React from 'react';
import {
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Dashboard as DashboardIcon,
  Terminal as TerminalIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  ExitToApp as ExitToAppIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

interface SidebarItem {
  text: string;
  icon: React.ReactNode;
  path: string;
}

const mainItems: SidebarItem[] = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Commands', icon: <TerminalIcon />, path: '/commands' },
  { text: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
];

const secondaryItems: SidebarItem[] = [
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  { text: 'Help', icon: <HelpIcon />, path: '/help' },
  { text: 'Logout', icon: <ExitToAppIcon />, path: '/logout' },
];

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onClose }) => {
  const theme = useTheme();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {mainItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={RouterLink}
              to={item.path}
              selected={location.pathname === item.path}
              onClick={isMobile ? onClose : undefined}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        {secondaryItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={RouterLink}
              to={item.path}
              selected={location.pathname === item.path}
              onClick={isMobile ? onClose : undefined}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <>
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Sidebar;
