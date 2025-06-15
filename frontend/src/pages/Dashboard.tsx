import React, { useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  Alert,
  Button,
  useTheme,
  alpha,
  Skeleton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Terminal as TerminalIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface Stats {
  totalCommands: number;
  successfulExecutions: number;
  failedExecutions: number;
  warnings: number;
}

interface RecentCommand {
  id: string;
  name: string;
  status: 'success' | 'failed' | 'running' | 'pending';
  timestamp: string;
  duration?: number;
}

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuth();

  // Fetch dashboard stats
  const {
    data: stats,
    isLoading: isLoadingStats,
    error: statsError,
    refetch: refetchStats
  } = useQuery<Stats>({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const response = await fetch('/api/stats');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });

  // Fetch recent commands
  const {
    data: recentCommands,
    isLoading: isLoadingCommands,
    error: commandsError,
    refetch: refetchRecentCommands
  } = useQuery<RecentCommand[]>({
    queryKey: ['recentCommands'],
    queryFn: async () => {
      const response = await fetch('/api/commands/recent');
      if (!response.ok) {
        throw new Error('Failed to fetch recent commands');
      }
      return response.json();
    },
  });

  const handleRefresh = useCallback(() => {
    refetchStats();
    refetchRecentCommands();
  }, [refetchStats, refetchRecentCommands]);

  const getStatusIcon = useCallback((status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <CircularProgress size={20} />;
      case 'pending':
        return <InfoIcon color="info" />;
      default:
        return <WarningIcon color="warning" />;
    }
  }, []);

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleString();
  }, []);

  const renderStatCard = useCallback(({ title, value, icon, color }: StatCardProps) => (
    <Box sx={{ height: '100%' }}>
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          borderLeft: `4px solid ${color}`,
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme.shadows[8],
          },
        }}
      >
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography color="textSecondary" variant="subtitle2">
              {title}
            </Typography>
            <Box
              sx={{
                p: 1,
                borderRadius: '50%',
                backgroundColor: alpha(color, 0.1),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                '& svg': {
                  color: color,
                  fontSize: 20
                }
              }}
            >
              {icon}
            </Box>
          </Box>
          {isLoadingStats ? (
            <Skeleton variant="rectangular" width="60%" height={32} />
          ) : (
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  ), [theme, alpha, isLoadingStats]);

  const statCards: StatCardProps[] = useMemo(() => [
    {
      title: 'Total Commands',
      value: stats?.totalCommands ?? '--',
      icon: <TerminalIcon />,
      color: theme.palette.primary.main
    },
    {
      title: 'Successful Executions',
      value: stats?.successfulExecutions ?? '--',
      icon: <CheckCircleIcon />,
      color: theme.palette.success.main
    },
    {
      title: 'Failed Executions',
      value: stats?.failedExecutions ?? '--',
      icon: <ErrorIcon />,
      color: theme.palette.error.main
    },
    {
      title: 'Warnings',
      value: stats?.warnings ?? '--',
      icon: <WarningIcon />,
      color: theme.palette.warning.main
    }
  ], [stats, theme]);

  if (isLoadingStats || isLoadingCommands) {
    return (
      <Box p={3}>
        <Skeleton variant="rectangular" width="100%" height={200} />
      </Box>
    );
  }

  const error = statsError || commandsError;
  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome back, {user?.username}!
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        Here's what's happening with your commands and reports.
      </Typography>

      {/* Stats Cards */}
      <Box sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: '1fr 1fr',
          md: 'repeat(4, 1fr)'
        },
        gap: 3,
        mb: 4
      }}>
        {statCards.map((statCard, index) => (
          <Box key={index}>
            {renderStatCard(statCard)}
          </Box>
        ))}
      </Box>

      {/* Recent Commands */}
      <Box sx={{ mb: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">Recent Commands</Typography>
            <Button
              size="small"
              color="primary"
              endIcon={<RefreshIcon fontSize="small" />}
              onClick={handleRefresh}
              disabled={isLoadingCommands}
            >
              Refresh
            </Button>
          </Box>

          {isLoadingCommands ? (
            <Box>
              {[1, 2, 3].map((i) => (
                <Box key={i} sx={{ mb: 2 }}>
                  <Skeleton variant="rectangular" width="100%" height={60} />
                </Box>
              ))}
            </Box>
          ) : commandsError ? (
            <Alert severity="error">
              Error loading recent commands: {commandsError ? String(commandsError) : 'Unknown error'}
            </Alert>
          ) : (
            <List>
              {recentCommands?.map((command) => (
                <React.Fragment key={command.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(command.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={command.name}
                      secondary={`${formatDate(command.timestamp)} • ${command.duration ? `${command.duration}s` : '--'}`}
                    />
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => {
                        // TODO: Navigate to command details
                        console.log('View command:', command.id);
                      }}
                    >
                      View Details
                    </Button>
                  </ListItem>
                  <Divider component="li" />
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard;
