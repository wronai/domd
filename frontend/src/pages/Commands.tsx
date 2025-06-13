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
  Add as AddIcon,
  Terminal as TerminalIcon
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

  // State for command menu and dialogs
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCommand, setSelectedCommand] = useState<Command | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning',
  });

  // State for table pagination and sorting
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [orderBy, setOrderBy] = useState<keyof Command>('createdAt');
  
  // State for filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

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
      const response = await fetch(
        `/api/commands?page=${page + 1}&limit=${limit}&search=${encodeURIComponent(
          searchTerm
        )}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch commands');
      }
      return response.json();
    },
    keepPreviousData: true,
  });

  // Extract commands array with fallback to empty array
  const commands = commandsData?.data || [];

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
    if (!selectedCommand) return;

    try {
      await deleteCommandMutation.mutateAsync(selectedCommand.id);
      setDeleteDialogOpen(false);
      setSnackbar({
        open: true,
        message: 'Command deleted successfully',
        severity: 'success',
      });
      // Invalidate the commands query to refetch the list
      queryClient.invalidateQueries({ queryKey: ['commands'] });
    } catch (error) {
      console.error('Error deleting command:', error);
      setSnackbar({
        open: true,
        message: 'Failed to delete command',
        severity: 'error',
      });
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
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Commands
        </Typography>
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
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" alignItems="center">
          <TextField
            variant="outlined"
            size="small"
            placeholder="Search commands..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            fullWidth
          />
          <Box ml={2}>
            <Button
              variant="outlined"
              startIcon={<FilterListIcon />}
              sx={{ ml: 1 }}
            >
              Filters
            </Button>
            <IconButton onClick={() => refetch()} sx={{ ml: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>
      </Paper>


      {/* Commands table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 300px)' }}>
          <Table stickyHeader aria-label="commands table" size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell>Last Run</TableCell>
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
                    <Alert severity="error" sx={{ mb: 2 }}>
                      Error loading commands
                    </Alert>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => refetch()}
                    >
                      Retry
                    </Button>
                  </TableCell>
                </TableRow>
              ) : commands.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                    <TerminalIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" color="textSecondary" gutterBottom>
                      No commands found
                    </Typography>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {searchTerm ? 'No commands match your search' : 'Get started by creating a new command'}
                    </Typography>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<AddIcon />}
                      onClick={() => navigate('/commands/new')}
                    >
                      Create Command
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                commands.map((command) => (
                  <TableRow
                    key={command.id}
                    hover
                    sx={{ '&:hover': { cursor: 'pointer' } }}
                  >
                    <TableCell>
                      <Typography variant="subtitle2">{command.name}</Typography>
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
                        {command.tags && command.tags.length > 2 && (
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
                        color={getStatusChipColor(command.status) as any}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                        <Tooltip title="Run">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRunCommand(command.id);
                            }}
                            disabled={runCommandMutation.isLoading}
                          >
                            <PlayArrowIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMenuOpen(e, command);
                          }}
                        >
                          <MoreVertIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={commandsData?.total || 0}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Menu for command actions */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={(e) => e.stopPropagation()}
      >
        <MenuItem onClick={() => selectedCommand && handleViewDetails(selectedCommand.id)}>
          <ListItemIcon>
            <TerminalIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => selectedCommand && handleRunCommand(selectedCommand.id)}
          disabled={runCommandMutation.isLoading}
        >
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
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
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
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
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
