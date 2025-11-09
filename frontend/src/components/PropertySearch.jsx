import React, { useState } from 'react';
import {
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Grid,
  MenuItem,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const PropertySearch = () => {
  const [formData, setFormData] = useState({
    address: '',
    property_type: '',
    bedrooms: '',
    bathrooms: '',
    parking: '',
    land_size: ''
  });

  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.address.trim()) {
      setError('Please enter a property address');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        address: formData.address,
        property_type: formData.property_type || null,
        bedrooms: formData.bedrooms ? parseInt(formData.bedrooms) : null,
        bathrooms: formData.bathrooms ? parseInt(formData.bathrooms) : null,
        parking: formData.parking ? parseInt(formData.parking) : null,
        land_size: formData.land_size ? parseFloat(formData.land_size) : null
      };

      const response = await axios.post(`${API_URL}/api/estimate-price`, payload);
      setResult(response.data);
    } catch (err) {
      console.error('Error estimating price:', err);
      setError('Failed to estimate property price. Please ensure the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0
    }).format(value);
  };

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
        <Typography variant="h5" gutterBottom>
          Property Price Estimator
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Get an instant estimate of any Australian property's market value
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Property Address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="e.g., 123 Smith Street, Melbourne VIC 3000"
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Property Type"
                name="property_type"
                value={formData.property_type}
                onChange={handleInputChange}
              >
                <MenuItem value="">Select type (optional)</MenuItem>
                <MenuItem value="house">House</MenuItem>
                <MenuItem value="apartment">Apartment</MenuItem>
                <MenuItem value="townhouse">Townhouse</MenuItem>
                <MenuItem value="unit">Unit</MenuItem>
                <MenuItem value="villa">Villa</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Bedrooms"
                name="bedrooms"
                value={formData.bedrooms}
                onChange={handleInputChange}
                inputProps={{ min: 0, max: 10 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Bathrooms"
                name="bathrooms"
                value={formData.bathrooms}
                onChange={handleInputChange}
                inputProps={{ min: 0, max: 10 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Parking Spaces"
                name="parking"
                value={formData.parking}
                onChange={handleInputChange}
                inputProps={{ min: 0, max: 10 }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Land Size (sqm)"
                name="land_size"
                value={formData.land_size}
                onChange={handleInputChange}
                inputProps={{ min: 0 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                type="submit"
                startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                disabled={isLoading}
              >
                {isLoading ? 'Estimating...' : 'Get Price Estimate'}
              </Button>
            </Grid>
          </Grid>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {result && (
        <Card sx={{ mt: 3 }} elevation={3}>
          <CardContent>
            <Typography variant="h5" gutterBottom color="primary">
              Price Estimate Results
            </Typography>

            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {result.address}
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={4}>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: '#e3f2fd' }}>
                    <Typography variant="body2" color="text.secondary">
                      Estimated Value
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {formatCurrency(result.estimated_price)}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: '#f3e5f5' }}>
                    <Typography variant="body2" color="text.secondary">
                      Price Range
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(result.price_range_min)}
                    </Typography>
                    <Typography variant="body2">to</Typography>
                    <Typography variant="h6">
                      {formatCurrency(result.price_range_max)}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: '#e8f5e9' }}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence Score
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {(result.confidence_score * 100).toFixed(0)}%
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Analysis
                </Typography>
                <Typography variant="body1" paragraph>
                  {result.explanation}
                </Typography>
              </Box>

              {result.market_trends && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Market Trends
                  </Typography>
                  <Grid container spacing={2}>
                    {result.market_trends.medianPrice && (
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Suburb Median
                        </Typography>
                        <Typography variant="body1">
                          {formatCurrency(result.market_trends.medianPrice)}
                        </Typography>
                      </Grid>
                    )}
                    {result.market_trends.annualGrowth !== undefined && (
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Annual Growth
                        </Typography>
                        <Typography variant="body1">
                          {result.market_trends.annualGrowth}%
                        </Typography>
                      </Grid>
                    )}
                    {result.market_trends.daysOnMarket && (
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Days on Market
                        </Typography>
                        <Typography variant="body1">
                          {result.market_trends.daysOnMarket}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              )}

              {result.sources && result.sources.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Data sources: {result.sources.join(', ')}
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PropertySearch;
