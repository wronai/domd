import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Divider,
  CircularProgress,
  Alert,
  Button,
  useTheme,
  alpha,
  Skeleton
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

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  // Fetch dashboard stats
  const { data: stats, isLoading: isLoadingStats, error: statsError, refetch: refetchStats } = useQuery<Stats>({
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
  const { data: recentCommands, isLoading: isLoadingCommands, error: commandsError } = useQuery<RecentCommand[]>({
    queryKey: ['recentCommands'],
    queryFn: async () => {
      const response = await fetch('/api/commands/recent');
      if (!response.ok) {
        throw new Error('Failed to fetch recent commands');
      }
      return response.json();
    },
  });

  const handleRefresh = () => {
    refetchStats();
    setLastRefreshed(new Date());
  };

  const getStatusIcon = (status: string) => {
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
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const renderStatCard = (title: string, value: number | string, icon: React.ReactNode, color: string) => (
    <Grid item xs={12} sm={6} md={3}>
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
              }}
            >
              {React.cloneElement(icon as React.ReactElement, {
                style: { color, fontSize: 20 }
              })}
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
    </Grid>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome back, {user?.username}!
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Here's what's happening with your commands and reports.
          </Typography>
        </Box>
        <Box display="flex" alignItems="center">
          {lastRefreshed && (
            <Typography variant="caption" color="textSecondary" sx={{ mr: 2 }}>
              Last updated: {lastRefreshed.toLocaleTimeString()}
            </Typography>
          )}
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={isLoadingStats}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {statsError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error loading dashboard data: {statsError.message}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {renderStatCard(
          'Total Commands',
          stats?.totalCommands ?? '--',
          <TerminalIcon />,
          theme.palette.primary.main
        )}
        {renderStatCard(
          'Successful Executions',
          stats?.successfulExecutions ?? '--',
          <CheckCircleIcon />,
          theme.palette.success.main
        )}
        {renderStatCard(
          'Failed Executions',
          stats?.failedExecutions ?? '--',
          <ErrorIcon />,
          theme.palette.error.main
        )}
        {renderStatCard(
          'Warnings',
          stats?.warnings ?? '--',
          <WarningIcon />,
          theme.palette.warning.main
        )}
      </Grid>

      <Grid container spacing={3}>
        <Grid item={true} xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">Recent Commands</Typography>
              <Button
                size="small"
                color="primary"
                endIcon={<RefreshIcon fontSize="small" />}
                onClick={() => {}}
              >
                Refresh
              </Button>
            </Box>

            {commandsError ? (
              <Alert severity="error">
                Error loading recent commands: {commandsError.message}
              </Alert>
            ) : isLoadingCommands ? (
              <Box>
                {[1, 2, 3].map((i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Skeleton variant="rectangular" height={60} />
                  </Box>
                ))}
              </Box>
            ) : recentCommands && recentCommands.length > 0 ? (
              <Box>
                {recentCommands.map((cmd) => (
                  <Card
                    key={cmd.id}
                    variant="outlined"
                    sx={{
                      mb: 1.5,
                      borderLeft: `3px solid ${
                        cmd.status === 'success'
                          ? theme.palette.success.main
                          : cmd.status === 'failed'
                            ? theme.palette.error.main
                            : theme.palette.warning.main
                      }`,
                      '&:hover': {
                        boxShadow: theme.shadows[2],
                      },
                    }}
                  >
                    <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1" component="div">
                            {cmd.name}
                          </Typography>
                          <Box display="flex" alignItems="center" mt={0.5}>
                            {getStatusIcon(cmd.status)}
                            <Typography
                              variant="caption"
                              color="textSecondary"
                              sx={{ ml: 0.5, textTransform: 'capitalize' }}
                            >
                              {cmd.status}
                            </Typography>
                            {cmd.duration && (
                              <Typography variant="caption" color="textSecondary" sx={{ ml: 1.5 }}>
                                {cmd.duration}s
                              </Typography>
                            )}
                          </Box>
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          {formatDate(cmd.timestamp)}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : (
              <Box textAlign="center" py={4}>
                <TerminalIcon color="action" sx={{ fontSize: 48, opacity: 0.5, mb: 1 }} />
                <Typography variant="subtitle1" color="textSecondary">
                  No recent commands found
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item={true} xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={2}>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                startIcon={<TerminalIcon />}
                onClick={() => {}}
              >
                Run New Command
              </Button>
              <Button
                variant="outlined"
                color="primary"
                fullWidth
                startIcon={<TerminalIcon />}
                onClick={() => {}}
              >
                View All Commands
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                fullWidth
                startIcon={<TerminalIcon />}
                onClick={() => {}}
              >
                View Reports
              </Button>
            </Box>

            <Box mt={4}>
              <Typography variant="subtitle2" gutterBottom>
                System Status
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box>
                {/* Add system status indicators here */}
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">API Status:</Typography>
                  <Box display="flex" alignItems="center">
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'success.main',
                        mr: 1
                      }}
                    />
                    <Typography variant="body2" color="textSecondary">Operational</Typography>
                  </Box>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Database:</Typography>
                  <Box display="flex" alignItems="center">
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'success.main',
                        mr: 1
                      }}
                    />
                    <Typography variant="body2" color="textSecondary">Connected</Typography>
                  </Box>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Last Scan:</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {new Date().toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
