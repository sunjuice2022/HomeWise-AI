import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import {
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import ChatInterface from './components/ChatInterface';
import PropertySearch from './components/PropertySearch';
import BuyingPowerCalculator from './components/BuyingPowerCalculator';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: '20px' }}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <AppBar position="static" elevation={2}>
          <Toolbar>
            <HomeIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              HomeWise AI - Property Intelligence
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Paper elevation={3}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              indicatorColor="primary"
              textColor="primary"
            >
              <Tab label="Chat Assistant" />
              <Tab label="Property Price Estimator" />
              <Tab label="Buying Power Calculator" />
            </Tabs>
          </Paper>

          <TabPanel value={activeTab} index={0}>
            <ChatInterface />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <PropertySearch />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <BuyingPowerCalculator />
          </TabPanel>

          <Box sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>
            <Typography variant="body2">
              © 2024 HomeWise AI - Powered by AI for Australian Property Buyers
            </Typography>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
