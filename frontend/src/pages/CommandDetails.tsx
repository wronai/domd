import React, { useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { alpha, useTheme } from '@mui/material/styles';
import type { Theme, Palette } from '@mui/material/styles';
import {
  Box,
  Typography,
  Paper,
  Button,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  TextField,
  Snackbar
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayArrowIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Code as CodeIcon,
  Info as InfoIcon,
  History as HistoryIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  ContentCopy as ContentCopyIcon,
  Terminal as TerminalIcon,
  HelpOutline as HelpOutlineIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface CommandRunResponse {
  id: string;
  status: 'success' | 'failed' | 'running';
  output: string;
  error?: string;
  timestamp: string;
}

interface CommandDeleteResponse {
  success: boolean;
  message: string;
}

interface Execution {
  id: string;
  status: 'success' | 'failed' | 'running' | 'pending';
  startedAt: string;
  finishedAt?: string;
  duration?: number;
  output?: string;
  error?: string;
}

interface CommandDetails {
  id: string;
  name: string;
  description: string;
  command: string;
  category: string;
  tags: string[];
  workingDirectory: string;
  timeout: number;
  environment: Record<string, string>;
  createdAt: string;
  updatedAt: string;
  lastRun?: {
    id: string;
    status: 'success' | 'failed' | 'running' | 'pending';
    startedAt: string;
    finishedAt?: string;
    duration?: number;
    output?: string;
    error?: string;
  };
  executionHistory: Execution[];
}

// Extend the theme to include custom palette colors
declare module '@mui/material/styles' {
  interface Palette {
    default: {
      main: string;
      light: string;
      dark: string;
    };
  }

  interface PaletteOptions {
    default?: {
      main?: string;
      light?: string;
      dark?: string;
    };
  }
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`command-tabpanel-${index}`}
      aria-labelledby={`command-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const a11yProps = (index: number) => ({
  id: `command-tab-${index}`,
  'aria-controls': `command-tabpanel-${index}`,
});

const CommandDetails: React.FC = () => {
  const theme = useTheme();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  // State management
  const [tabValue, setTabValue] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    details: true,
    settings: true,
    execution: true,
  });
  const [autoScrollOutput, setAutoScrollOutput] = useState(true);
  const outputRef = useRef<HTMLDivElement>(null);

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Fetch command details
  const { data: command, isLoading, error, refetch } = useQuery<CommandDetails, Error>({
    queryKey: ['command', id],
    queryFn: async () => {
      const response = await fetch(`/api/commands/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch command details');
      }
      return response.json();
    },
    enabled: !!id,
  });

  const commandData = command || {} as CommandDetails;

  // Run command mutation
  const runCommandMutation = useMutation<CommandRunResponse, Error, void>({
    mutationFn: async () => {
      const response = await fetch(`/api/commands/${id}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to run command');
      }

      return response.json();
    },
    onSuccess: () => {
      refetch();
      setSnackbar({
        open: true,
        message: 'Command started successfully',
        severity: 'success',
      });
    },
    onError: (error: Error) => {
      setSnackbar({
        open: true,
        message: `Error running command: ${error.message}`,
        severity: 'error',
      });
    },
  });

  // Delete command mutation
  const deleteCommandMutation = useMutation<CommandDeleteResponse, Error, void>({
    mutationFn: async () => {
      const response = await fetch(`/api/commands/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete command');
      }

      return response.json();
    },
    onSuccess: () => {
      navigate('/commands');
      setSnackbar({
        open: true,
        message: 'Command deleted successfully',
        severity: 'success',
      });
    },
    onError: (error: Error) => {
      setSnackbar({
        open: true,
        message: `Error deleting command: ${error.message}`,
        severity: 'error',
      });
    },
  });

  // Format date helper
  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleString();
  }, []);

  // Format duration helper
  const formatDuration = useCallback((seconds?: number) => {
    if (!seconds) return '--';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    const parts = [];
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0 || hours > 0) parts.push(`${minutes}m`);
    parts.push(`${secs}s`);

    return parts.join(' ');
  }, []);

  // Get status icon helper
  const getStatusIcon = useCallback((status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <CircularProgress size={24} />;
      default:
        return <HelpOutlineIcon color="disabled" />;
    }
  }, []);

  // Get status chip color helper
  const getStatusChipColor = useCallback((status?: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'info';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  }, []);

  // Handle copy to clipboard
  const handleCopyToClipboard = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
    setSnackbar({
      open: true,
      message: 'Copied to clipboard!',
      severity: 'success',
    });
  }, []);

  // Handle snackbar close
  const handleCloseSnackbar = useCallback(() => {
    setSnackbar(prev => ({ ...prev, open: false }));
  }, []);

  // Handle tab change
  const handleTabChange = useCallback((event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  }, []);

  // Toggle section expansion
  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);

  // Handle run command
  const handleRunCommand = useCallback(() => {
    runCommandMutation.mutate();
  }, [runCommandMutation]);

  // Handle delete command
  const handleDeleteCommand = useCallback(() => {
    if (window.confirm('Are you sure you want to delete this command?')) {
      deleteCommandMutation.mutate();
    }
  }, [deleteCommandMutation]);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }


  if (error) {
    return (
      <Alert severity="error">
        Error loading command: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  // ... rest of the component code ...

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Your JSX here */}
    </Box>
  );
};

export default CommandDetails;
