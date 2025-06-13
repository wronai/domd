import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Reports: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Reports
        </Typography>
        <Typography>
          Reports dashboard will be available soon.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Reports;
