import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Tooltip,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  CircularProgress,
  Alert,
  Snackbar,
  useTheme,
  alpha
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface Command {
  id: string;
  name: string;
  description: string;
  command: string;
  category: string;
  tags: string[];
  lastRun?: string;
  status?: 'success' | 'failed' | 'running' | 'pending';
  createdAt: string;
  updatedAt: string;
}

type CommandRunResponse = {
  id: string;
  status: 'success' | 'failed' | 'running' | 'pending';
  startedAt: string;
  finishedAt?: string;
  output?: string;
  error?: string;
};

type CommandDeleteResponse = {
  success: boolean;
  message: string;
};

interface CommandListResponse {
  data: Command[];
  total: number;
  page: number;
  limit: number;
}

const Commands: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Add missing state for menu anchor
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [selectedCommand, setSelectedCommand] = React.useState<Command | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [snackbar, setSnackbar] = React.useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning'
  });

  // State for pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // State for sorting
  const [orderBy, setOrderBy] = useState<keyof Command>('name');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');

  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  // State for command menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCommand, setSelectedCommand] = useState<Command | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' | 'warning' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Fetch commands
  const {
    data: commandsData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery<CommandListResponse>({
    queryKey: ['commands', page, rowsPerPage, orderBy, order, searchTerm, statusFilter, categoryFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        limit: rowsPerPage.toString(),
        sortBy: orderBy,
        order,
        search: searchTerm,
        ...(statusFilter !== 'all' && { status: statusFilter }),
        ...(categoryFilter !== 'all' && { category: categoryFilter }),
      });

      const response = await fetch(`/api/commands?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch commands');
      }
      return response.json();
    },
    keepPreviousData: true,
  });

  // Run command mutation
  const runCommandMutation = useMutation(
    (commandId: string) =>
      fetch(`/api/commands/${commandId}/run`, { method: 'POST' })
        .then(res => {
          if (!res.ok) throw new Error('Failed to run command');
          return res.json();
        }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['commands']);
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
  ) as UseMutationResult<CommandRunResponse, Error, string, unknown>;

  // Delete command mutation
  const deleteCommandMutation = useMutation<CommandDeleteResponse, Error, string>(
    async (commandId: string) => {
      const response = await fetch(`/api/commands/${commandId}`, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete command');
      }
      return response.json();
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['commands'] });
        setSnackbar({
          open: true,
          message: 'Command deleted successfully',
          severity: 'success'
        });
        setDeleteDialogOpen(false);
      },
      onError: (error: Error) => {
        setSnackbar({
          open: true,
          message: error.message || 'Failed to delete command',
          severity: 'error'
        });
      },
    }
  ) as UseMutationResult<CommandDeleteResponse, Error, string, unknown>;

  // Handle sort request
  const handleRequestSort = (property: keyof Command) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  // Handle change page
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  // Handle change rows per page
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle search
  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  // Handle menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, command: Command) => {
    setAnchorEl(event.currentTarget);
    setSelectedCommand(command);
  };

  // Handle menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCommand(null);
  };

  // Handle run command
  const handleRunCommand = async (commandId: string) => {
    try {
      await runCommandMutation.mutateAsync(commandId);
      handleMenuClose();
    } catch (error) {
      console.error('Error running command:', error);
      setSnackbar({
        open: true,
        message: 'Failed to run command',
        severity: 'error'
      });
    }
  };

  // Handle edit command
  const handleEditCommand = (commandId: string) => {
    navigate(`/commands/${commandId}/edit`);
    handleMenuClose();
  };

  // Handle view command details
  const handleViewDetails = (commandId: string) => {
    navigate(`/commands/${commandId}`);
    handleMenuClose();
  };

  // Handle delete command confirmation
  const handleDeleteClick = () => {
    if (selectedCommand) {
      setDeleteDialogOpen(true);
    }
    handleMenuClose();
  };

  // Handle confirm delete
  const handleConfirmDelete = async () => {
    if (selectedCommand) {
      try {
        await deleteCommandMutation.mutateAsync(selectedCommand.id);
      } catch (error) {
        console.error('Error deleting command:', error);
      }
    }
  };

  // Handle close delete dialog
  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setSelectedCommand(null);
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
        return <CheckCircleIcon fontSize="small" />;
      case 'failed':
        return <ErrorIcon fontSize="small" />;
      case 'running':
        return <CircularProgress size={16} />;
      case 'pending':
        return <ScheduleIcon fontSize="small" />;
      default:
        return <InfoIcon fontSize="small" />;
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Commands
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage and execute your project commands
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/commands/new')}
        >
          New Command
        </Button>
      </Box>

      {/* Search and filter bar */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center' }}>
        <TextField
          variant="outlined"
          size="small"
          placeholder="Search commands..."
          value={searchTerm}
          onChange={handleSearch}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, mr: 2 }}
        />

        <Button
          variant="outlined"
          startIcon={<FilterListIcon />}
          sx={{ mr: 1 }}
        >
          Filters
        </Button>

        <Tooltip title="Refresh">
          <IconButton onClick={() => refetch()}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Paper>

      {/* Commands table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 300px)' }}>
          <Table stickyHeader aria-label="commands table" size="medium">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'name'}
                    direction={orderBy === 'name' ? order : 'asc'}
                    onClick={() => handleRequestSort('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'lastRun'}
                    direction={orderBy === 'lastRun' ? order : 'desc'}
                    onClick={() => handleRequestSort('lastRun')}
                  >
                    Last Run
                  </TableSortLabel>
                </TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      Loading commands...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : isError ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Alert severity="error">
                      Error loading commands: {error instanceof Error ? error.message : 'Unknown error'}
                    </Alert>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => refetch()}
                      sx={{ mt: 2 }}
                    >
                      Retry
                    </Button>
                  </TableCell>
                </TableRow>
              ) : commandsData?.data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                    <Box sx={{ maxWidth: 400, mx: 'auto' }}>
                      <TerminalIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary" gutterBottom>
                        No commands found
                      </Typography>
                      <Typography variant="body2" color="textSecondary" paragraph>
                        {searchTerm
                          ? 'No commands match your search. Try a different search term.'
                          : 'Get started by creating a new command.'}
                      </Typography>
                      <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={() => navigate('/commands/new')}
                      >
                        Create Command
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                commandsData?.data.map((command) => (
                  <TableRow
                    key={command.id}
                    hover
                    sx={{ '&:hover': { backgroundColor: alpha(theme.palette.primary.light, 0.04) } }}
                  >
                    <TableCell>
                      <Typography variant="subtitle2">
                        {command.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary" noWrap>
                        {command.description || 'No description'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={command.category || 'Uncategorized'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {command.tags?.slice(0, 2).map((tag) => (
                          <Chip
                            key={tag}
                            label={tag}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                        {command.tags?.length > 2 && (
                          <Chip
                            label={`+${command.tags.length - 2}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {command.lastRun ? formatDate(command.lastRun) : 'Never'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(command.status)}
                        label={command.status || 'unknown'}
                        color={getStatusChipColor(command.status)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <Tooltip title="Run">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleRunCommand(command.id)}
                            disabled={runCommandMutation.isLoading}
                          >
                            <PlayArrowIcon />
                          </IconButton>
                        </Tooltip>
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, command)}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={commandsData?.total || 0}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Command menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
        PaperProps={{
          elevation: 1,
          sx: {
            minWidth: 180,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => selectedCommand && handleViewDetails(selectedCommand.id)}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedCommand && handleRunCommand(selectedCommand.id)}>
          <ListItemIcon>
            <PlayArrowIcon fontSize="small" color="primary" />
          </ListItemIcon>
          <ListItemText>Run Command</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedCommand && handleEditCommand(selectedCommand.id)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDeleteClick}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Command
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete the command "{selectedCommand?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteCommandMutation.isLoading}
            startIcon={deleteCommandMutation.isLoading ? <CircularProgress size={20} /> : null}
          >
            {deleteCommandMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

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

export default Commands;
