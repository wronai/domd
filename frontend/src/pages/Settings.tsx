import React from 'react';
import { Box, Typography, Paper, TextField, Button } from '@mui/material';

const Settings: React.FC = () => {
  const [settings, setSettings] = React.useState({
    theme: 'light',
    notifications: true,
    language: 'en',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>

        <Box component="form" sx={{ mt: 3 }}>
          <TextField
            select
            fullWidth
            label="Theme"
            name="theme"
            value={settings.theme}
            onChange={handleChange}
            SelectProps={{ native: true }}
            margin="normal"
            variant="outlined"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System Default</option>
          </TextField>


          <TextField
            select
            fullWidth
            label="Language"
            name="language"
            value={settings.language}
            onChange={handleChange}
            SelectProps={{ native: true }}
            margin="normal"
            variant="outlined"
          >
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </TextField>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => console.log('Settings saved', settings)}
            >
              Save Changes
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default Settings;
