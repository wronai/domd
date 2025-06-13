import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
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
  Snackbar,
  useTheme,
  alpha
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
  Terminal as TerminalIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow, format } from 'date-fns';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

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
  executionHistory: Array<{
    id: string;
    status: 'success' | 'failed' | 'running' | 'pending';
    startedAt: string;
    finishedAt?: string;
    duration?: number;
  }>;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`command-details-tabpanel-${index}`}
      aria-labelledby={`command-details-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `command-details-tab-${index}`,
    'aria-controls': `command-details-tabpanel-${index}`,
  };
}

const CommandDetails: React.FC = () => {
  const theme = useTheme();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning'
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Fetch command details
  const {
    data: command,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery<CommandDetails>({
    queryKey: ['command', id],
    queryFn: async () => {
      const response = await fetch(`/api/commands/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch command details');
      }
      return response.json();
    },
    refetchInterval: command?.lastRun?.status === 'running' ? 2000 : false,
  });

  // Run command mutation
  const runCommandMutation = useMutation(
    () =>
      fetch(`/api/commands/${id}/run`, { method: 'POST' })
        .then(res => {
          if (!res.ok) throw new Error('Failed to run command');
          return res.json();
        }),
    {
      onSuccess: () => {
        refetch();
        setSnackbar({
          open: true,
          message: 'Command started successfully',
          severity: 'success'
        });
      },
      onError: (error: Error) => {
        setSnackbar({
          open: true,
          message: `Error running command: ${error.message}`,
          severity: 'error'
        });
      },
    }
  );

  // Delete command mutation
  const deleteCommandMutation = useMutation<CommandDeleteResponse, Error, void>(
    async () => {
      const response = await fetch(`/api/commands/${id}`, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete command');
      }
      return response.json();
    },
    {
      onSuccess: () => {
        setSnackbar({
          open: true,
          message: 'Command deleted successfully',
          severity: 'success',
        });
        navigate('/commands');
      },
      onError: (error: Error) => {
        setSnackbar({
          open: true,
          message: error.message || 'Failed to delete command',
          severity: 'error',
        });
      },
    }
  ) as UseMutationResult<CommandDeleteResponse, Error, void, unknown>;

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  // Handle run command
  const handleRunCommand = async () => {
    try {
      await runCommandMutation.mutateAsync(undefined);
    } catch (error) {
      console.error('Error running command:', error);
    }
  };

  // Handle edit command
  const handleEditCommand = () => {
    navigate(`/commands/${id}/edit`);
  };

  // Handle delete command
  const handleDeleteCommand = () => {
    if (window.confirm('Are you sure you want to delete this command? This action cannot be undone.')) {
      deleteCommandMutation.mutate();
    }
  };

  // Handle copy to clipboard
  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSnackbar({
      open: true,
      message: 'Copied to clipboard',
      severity: 'success'
    });
  };

  // Handle close snackbar
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Get status chip color
  const getStatusChipColor = (status?: string) => {
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
  };

  // Get status icon
  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon />;
      case 'failed':
        return <ErrorIcon />;
      case 'running':
        return <CircularProgress size={16} />;
      case 'pending':
        return <ScheduleIcon />;
      default:
        return <InfoIcon />;
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'PPpp');
  };

  // Format duration
  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--';
    if (seconds < 1) return '<1s';
    if (seconds < 60) return `${Math.round(seconds)}s`;

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (isError || !command) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        Error loading command: {error instanceof Error ? error.message : 'Unknown error'}
        <Box mt={2}>
          <Button
            variant="outlined"
            onClick={() => refetch()}
            startIcon={<RefreshIcon />}
          >
            Retry
          </Button>
        </Box>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header with back button and actions */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box display="flex" alignItems="center">
          <IconButton onClick={() => navigate('/commands')} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" component="h1">
              {command.name}
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {command.description || 'No description provided'}
            </Typography>
          </Box>
        </Box>
        <Box>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteCommand}
            disabled={deleteCommandMutation.isLoading}
            sx={{ mr: 1 }}
          >
            {deleteCommandMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={handleEditCommand}
            sx={{ mr: 1 }}
          >
            Edit
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={
              runCommandMutation.isLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <PlayArrowIcon />
              )
            }
            onClick={handleRunCommand}
            disabled={runCommandMutation.isLoading || command.lastRun?.status === 'running'}
          >
            {command.lastRun?.status === 'running' ? 'Running...' : 'Run Command'}
          </Button>
        </Box>
      </Box>

      {/* Status card */}
      {command.lastRun && (
        <Card sx={{ mb: 3, borderLeft: `4px solid ${theme.palette[getStatusChipColor(command.lastRun.status)].main}` }}>
          <CardHeader
            avatar={
              <Avatar sx={{ bgcolor: theme.palette[getStatusChipColor(command.lastRun.status)].light }}>
                {getStatusIcon(command.lastRun.status)}
              </Avatar>
            }
            title={
              <Box display="flex" alignItems="center">
                <Typography variant="h6" component="span" sx={{ mr: 1 }}>
                  {command.lastRun.status === 'success'
                    ? 'Last run completed successfully'
                    : command.lastRun.status === 'failed'
                      ? 'Last run failed'
                      : command.lastRun.status === 'running'
                        ? 'Command is running...'
                        : 'Command status'}
                </Typography>
                <Chip
                  label={command.lastRun.status}
                  size="small"
                  color={getStatusChipColor(command.lastRun.status)}
                  variant="outlined"
                />
              </Box>
            }
            subheader={
              <Typography variant="body2" color="textSecondary">
                {command.lastRun.status === 'running'
                  ? `Started ${formatDistanceToNow(new Date(command.lastRun.startedAt), { addSuffix: true })}`
                  : command.lastRun.finishedAt
                    ? `Completed ${formatDistanceToNow(new Date(command.lastRun.finishedAt), { addSuffix: true })}`
                    : 'No execution history'}
                {command.lastRun.duration !== undefined && (
                  <span> • Took {formatDuration(command.lastRun.duration)}</span>
                )}
              </Typography>
            }
            action={
              <IconButton onClick={() => refetch()}>
                <RefreshIcon />
              </IconButton>
            }
          />
          {(command.lastRun.output || command.lastRun.error) && (
            <CardContent sx={{ pt: 0, '&:last-child': { pb: 2 } }}>
              <Box
                sx={{
                  backgroundColor: theme.palette.mode === 'dark' ? '#1E1E1E' : '#f5f5f5',
                  borderRadius: 1,
                  p: 2,
                  position: 'relative',
                }}
              >
                <IconButton
                  size="small"
                  onClick={() => handleCopyToClipboard(command.lastRun?.output || command.lastRun?.error || '')}
                  sx={{ position: 'absolute', top: 8, right: 8, color: 'text.secondary' }}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
                <SyntaxHighlighter
                  language="bash"
                  style={atomOneDark}
                  customStyle={{
                    margin: 0,
                    padding: 0,
                    background: 'transparent',
                    fontSize: '0.85rem',
                    fontFamily: '\'Roboto Mono\', monospace',
                  }}
                  wrapLines={true}
                  wrapLongLines={true}
                >
                  {command.lastRun.error || command.lastRun.output || 'No output available'}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          )}
        </Card>
      )}

      {/* Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" {...a11yProps(0)} />
          <Tab label="Command" {...a11yProps(1)} />
          <Tab label="History" {...a11yProps(2)} />
        </Tabs>
      </Paper>

      {/* Tab panels */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader
                title="Command Details"
                avatar={
                  <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                    <InfoIcon />
                  </Avatar>
                }
              />
              <CardContent>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Name"
                      secondary={command.name || '--'}
                      secondaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Description"
                      secondary={command.description || 'No description provided'}
                      secondaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Category"
                      secondary={
                        <Chip
                          label={command.category || 'Uncategorized'}
                          size="small"
                          variant="outlined"
                        />
                      }
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Tags"
                      secondary={
                        command.tags && command.tags.length > 0 ? (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                            {command.tags.map(tag => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        ) : (
                          'No tags'
                        )
                      }
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Created"
                      secondary={formatDate(command.createdAt)}
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Last Updated"
                      secondary={formatDate(command.updatedAt)}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader
                title="Execution Settings"
                avatar={
                  <Avatar sx={{ bgcolor: theme.palette.secondary.main }}>
                    <TerminalIcon />
                  </Avatar>
                }
              />
              <CardContent>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Working Directory"
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 'calc(100% - 32px)' }}>
                            {command.workingDirectory || '--'}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => command.workingDirectory && handleCopyToClipboard(command.workingDirectory)}
                            sx={{ ml: 1 }}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText
                      primary="Timeout"
                      secondary={`${command.timeout || '--'} seconds`}
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem
                    button
                    onClick={() => toggleSection('environment')}
                    sx={{ '&:hover': { backgroundColor: 'transparent' } }}
                  >
                    <ListItemText
                      primary="Environment Variables"
                      secondary={`${Object.keys(command.environment || {}).length} variables`}
                    />
                    {expandedSection === 'environment' ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </ListItem>
                  <Collapse in={expandedSection === 'environment'} timeout="auto" unmountOnExit>
                    <Box sx={{ pl: 4, pr: 2, pb: 2 }}>
                      {Object.keys(command.environment || {}).length > 0 ? (
                        <List dense disablePadding>
                          {Object.entries(command.environment || {}).map(([key, value]) => (
                            <React.Fragment key={key}>
                              <ListItem sx={{ pl: 2, pr: 1, py: 0.5 }}>
                                <ListItemText
                                  primary={
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                        {key}
                                      </Typography>
                                      <IconButton
                                        size="small"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleCopyToClipboard(value);
                                        }}
                                        sx={{ ml: 1, p: 0.5 }}
                                      >
                                        <ContentCopyIcon fontSize="small" />
                                      </IconButton>
                                    </Box>
                                  }
                                  secondary={
                                    <Typography
                                      variant="body2"
                                      color="text.secondary"
                                      sx={{
                                        fontFamily: 'monospace',
                                        wordBreak: 'break-all',
                                        whiteSpace: 'pre-wrap'
                                      }}
                                    >
                                      {value}
                                    </Typography>
                                  }
                                  secondaryTypographyProps={{ component: 'div' }}
                                />
                              </ListItem>
                              <Divider component="li" sx={{ my: 0.5 }} />
                            </React.Fragment>
                          ))}
                        </List>
                      ) : (
                        <Typography variant="body2" color="textSecondary">
                          No environment variables defined
                        </Typography>
                      )}
                    </Box>
                  </Collapse>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardHeader
            title="Command"
            avatar={
              <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                <CodeIcon />
              </Avatar>
            }
            action={
              <Button
                variant="outlined"
                size="small"
                startIcon={<ContentCopyIcon />}
                onClick={() => handleCopyToClipboard(command.command)}
              >
                Copy
              </Button>
            }
          />
          <CardContent>
            <Box
              sx={{
                backgroundColor: theme.palette.mode === 'dark' ? '#1E1E1E' : '#f5f5f5',
                borderRadius: 1,
                p: 2,
                position: 'relative',
                '&:hover': {
                  '& .copy-button': {
                    opacity: 1,
                  },
                },
              }}
            >
              <IconButton
                size="small"
                className="copy-button"
                onClick={() => handleCopyToClipboard(command.command)}
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  opacity: 0,
                  transition: 'opacity 0.2s',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.08)',
                  },
                }}
              >
                <ContentCopyIcon fontSize="small" />
              </IconButton>
              <SyntaxHighlighter
                language="bash"
                style={atomOneDark}
                customStyle={{
                  margin: 0,
                  padding: 0,
                  background: 'transparent',
                  fontSize: '0.9rem',
                  fontFamily: '\'Roboto Mono\', monospace',
                }}
                wrapLines={true}
                wrapLongLines={true}
              >
                {command.command}
              </SyntaxHighlighter>
            </Box>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Card>
          <CardHeader
            title="Execution History"
            avatar={
              <Avatar sx={{ bgcolor: theme.palette.secondary.main }}>
                <HistoryIcon />
              </Avatar>
            }
            action={
              <Button
                variant="outlined"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
                disabled={command.lastRun?.status === 'running'}
              >
                Refresh
              </Button>
            }
          />
          <CardContent>
            {command.executionHistory && command.executionHistory.length > 0 ? (
              <List disablePadding>
                {command.executionHistory.map((execution) => (
                  <React.Fragment key={execution.id}>
                    <ListItem
                      button
                      onClick={() => navigate(`/executions/${execution.id}`)}
                      sx={{
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.04),
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {getStatusIcon(execution.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="body1" component="span">
                              {execution.status === 'success'
                                ? 'Completed successfully'
                                : execution.status === 'failed'
                                  ? 'Failed'
                                  : execution.status === 'running'
                                    ? 'In progress'
                                    : 'Pending'}
                            </Typography>
                            <Typography variant="body2" color="textSecondary" component="span">
                              {formatDate(execution.startedAt)}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box component="span" display="flex" justifyContent="space-between">
                            <Typography
                              component="span"
                              variant="body2"
                              color="textSecondary"
                            >
                              {execution.duration !== undefined ? (
                                `Took ${formatDuration(execution.duration)}`
                              ) : (
                                '--'
                              )}
                            </Typography>
                            <Typography
                              component="span"
                              variant="body2"
                              color="textSecondary"
                            >
                              {execution.finishedAt
                                ? `${formatDistanceToNow(new Date(execution.finishedAt), { addSuffix: true })}`
                                : 'In progress...'}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box textAlign="center" py={4}>
                <HistoryIcon sx={{ fontSize: 48, opacity: 0.2, mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No Execution History
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  This command hasn't been executed yet. Run it to see execution history.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<PlayArrowIcon />}
                  onClick={handleRunCommand}
                  disabled={runCommandMutation.isLoading || command.lastRun?.status === 'running'}
                >
                  {runCommandMutation.isLoading ? 'Running...' : 'Run Command'}
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CommandDetails;
