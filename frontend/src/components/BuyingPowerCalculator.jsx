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
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const BuyingPowerCalculator = () => {
  const [formData, setFormData] = useState({
    deposit: '',
    annual_income: '',
    monthly_expenses: '',
    other_income: '',
    dependents: '0',
    employment_type: 'full_time',
    existing_debts: ''
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

    if (!formData.deposit || !formData.annual_income) {
      setError('Please enter at least your deposit and annual income');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        deposit: parseFloat(formData.deposit),
        annual_income: parseFloat(formData.annual_income),
        monthly_expenses: formData.monthly_expenses ? parseFloat(formData.monthly_expenses) : 3000,
        other_income: formData.other_income ? parseFloat(formData.other_income) : 0,
        dependents: parseInt(formData.dependents),
        employment_type: formData.employment_type,
        existing_debts: formData.existing_debts ? parseFloat(formData.existing_debts) : 0
      };

      const response = await axios.post(`${API_URL}/api/calculate-buying-power`, payload);
      setResult(response.data);
    } catch (err) {
      console.error('Error calculating buying power:', err);
      setError('Failed to calculate buying power. Please ensure the backend server is running.');
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
          Buying Power Calculator
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Calculate how much you can borrow and what property price you can afford
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Deposit ($)"
                name="deposit"
                value={formData.deposit}
                onChange={handleInputChange}
                required
                inputProps={{ min: 0, step: 1000 }}
                helperText="Amount you have saved for deposit"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Annual Income ($)"
                name="annual_income"
                value={formData.annual_income}
                onChange={handleInputChange}
                required
                inputProps={{ min: 0, step: 1000 }}
                helperText="Your gross annual income"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Monthly Expenses ($)"
                name="monthly_expenses"
                value={formData.monthly_expenses}
                onChange={handleInputChange}
                inputProps={{ min: 0, step: 100 }}
                helperText="Your monthly living expenses"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Other Monthly Income ($)"
                name="other_income"
                value={formData.other_income}
                onChange={handleInputChange}
                inputProps={{ min: 0, step: 100 }}
                helperText="Rental income, investments, etc."
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Employment Type"
                name="employment_type"
                value={formData.employment_type}
                onChange={handleInputChange}
              >
                <MenuItem value="full_time">Full Time</MenuItem>
                <MenuItem value="part_time">Part Time</MenuItem>
                <MenuItem value="casual">Casual</MenuItem>
                <MenuItem value="self_employed">Self Employed</MenuItem>
                <MenuItem value="contract">Contract</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Dependents"
                name="dependents"
                value={formData.dependents}
                onChange={handleInputChange}
                inputProps={{ min: 0, max: 20 }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Existing Debt Repayments ($/month)"
                name="existing_debts"
                value={formData.existing_debts}
                onChange={handleInputChange}
                inputProps={{ min: 0, step: 100 }}
                helperText="Car loans, credit cards, HECS, etc."
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                type="submit"
                startIcon={isLoading ? <CircularProgress size={20} /> : <CalculateIcon />}
                disabled={isLoading}
              >
                {isLoading ? 'Calculating...' : 'Calculate Buying Power'}
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
              Your Buying Power
            </Typography>

            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Paper elevation={1} sx={{ p: 3, bgcolor: '#e8f5e9', textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Maximum Property Price
                  </Typography>
                  <Typography variant="h3" color="success.main" sx={{ my: 1 }}>
                    {formatCurrency(result.max_property_price)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    What you can afford to buy
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper elevation={1} sx={{ p: 3, bgcolor: '#e3f2fd', textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Maximum Loan Amount
                  </Typography>
                  <Typography variant="h3" color="primary" sx={{ my: 1 }}>
                    {formatCurrency(result.max_loan_amount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    How much you can borrow
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Monthly Repayment
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(result.monthly_repayment)}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Loan-to-Value Ratio
                  </Typography>
                  <Typography variant="h6">
                    {result.loan_to_value_ratio}%
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Stamp Duty
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(result.stamp_duty)}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Upfront Costs
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(result.total_upfront_costs)}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3 }}>
              <Alert severity={
                result.affordability_rating === 'Excellent' ? 'success' :
                result.affordability_rating === 'Good' ? 'info' :
                result.affordability_rating === 'Fair' ? 'warning' : 'error'
              }>
                <Typography variant="h6">
                  Affordability Rating: {result.affordability_rating}
                </Typography>
              </Alert>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Explanation
              </Typography>
              <Typography variant="body1" paragraph>
                {result.explanation}
              </Typography>
            </Box>

            {result.recommendations && result.recommendations.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <List>
                  {result.recommendations.map((recommendation, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircleIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={recommendation} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {result.assumptions && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Assumptions:</strong>
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Interest rate: {result.assumptions.interest_rate} |
                  Loan term: {result.assumptions.loan_term} |
                  Stress test rate: {result.assumptions.stress_test_rate}
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default BuyingPowerCalculator;
