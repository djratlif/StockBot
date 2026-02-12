import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { TrendingUp, TrendingDown, Timeline } from '@mui/icons-material';
import axios from 'axios';

interface ChartDataPoint {
  timestamp: string;
  total_value: number;
  cash_balance: number;
  total_return: number;
  total_return_percent: number;
}

interface HoldingBreakdown {
  symbol: string;
  quantity: number;
  market_value: number;
  percentage: number;
}

interface PerformanceMetrics {
  period_days: number;
  total_change: number;
  total_change_percent: number;
  data_points_count: number;
}

interface PortfolioChartData {
  data_points: ChartDataPoint[];
  holdings_breakdown: HoldingBreakdown[];
  performance_metrics: PerformanceMetrics;
}

const PortfolioChart: React.FC = () => {
  const [chartData, setChartData] = useState<PortfolioChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<number>(7);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number>(0);

  const fetchCurrentPrice = async () => {
    try {
      const response = await axios.get('/api/stocks/AAPL/price');
      setCurrentPrice(response.data.price);
    } catch (err) {
      console.error('Error fetching current price:', err);
    }
  };

  const fetchChartData = async () => {
    try {
      setError(null);
      const response = await axios.get(`/api/portfolio/chart-data?days=${timeRange}`);
      const data: PortfolioChartData = response.data;
      
      // Calculate percentages for holdings breakdown
      const totalValue = data.holdings_breakdown.reduce((sum, holding) => sum + holding.market_value, 0);
      data.holdings_breakdown = data.holdings_breakdown.map(holding => ({
        ...holding,
        percentage: totalValue > 0 ? (holding.market_value / totalValue) * 100 : 0
      }));
      
      setChartData(data);
      
      // Also fetch current price when updating chart data
      await fetchCurrentPrice();
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setError('Failed to load portfolio chart data');
    } finally {
      setLoading(false);
    }
  };

  const createPortfolioSnapshot = async () => {
    try {
      await axios.post('/api/portfolio/snapshot');
      // Refresh chart data after creating snapshot
      await fetchChartData();
    } catch (err) {
      console.error('Error creating portfolio snapshot:', err);
    }
  };

  useEffect(() => {
    fetchChartData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchChartData();
    }, 30000);
    
    setRefreshInterval(interval);
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [timeRange]);

  useEffect(() => {
    // Create initial snapshot if no data points exist
    if (chartData && chartData.data_points.length === 0) {
      createPortfolioSnapshot();
    }
  }, [chartData]);

  const handleTimeRangeChange = (event: any) => {
    setTimeRange(event.target.value);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!chartData) {
    return null;
  }

  // Prepare data for holdings value chart (focused on stock holdings only, excluding cash)
  const holdingsValueData = {
    x: chartData.data_points.map(point => new Date(point.timestamp)),
    y: chartData.data_points.map(point => point.total_value - point.cash_balance),
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'Holdings Value',
    line: { color: '#1976d2', width: 3 },
    marker: { size: 8, color: '#1976d2' },
    fill: 'tonexty' as const,
    fillcolor: 'rgba(25, 118, 210, 0.1)',
    customdata: chartData.data_points.map(point => [
      ((point.total_value - point.cash_balance) / 7).toFixed(2), // Historical share price from snapshot
      7, // Number of shares
      currentPrice // Current real market price (AAPL)
    ]),
    hovertemplate: '<b>AAPL Holdings</b><br>' +
                   'Time: %{x}<br>' +
                   'Historical Price: $%{customdata[0]}<br>' +
                   'Current Market Price: $%{customdata[2]:.2f}<br>' +
                   'Shares Owned: %{customdata[1]}<br>' +
                   'Total Value: $%{y:.2f}<extra></extra>'
  };

  // Prepare data for holdings pie chart
  const holdingsPieData = {
    values: chartData.holdings_breakdown.map(holding => holding.market_value),
    labels: chartData.holdings_breakdown.map(holding => holding.symbol),
    type: 'pie' as const,
    textinfo: 'label+percent' as const,
    textposition: 'auto' as const,
    hovertemplate: '<b>%{label}</b><br>Value: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
  };

  // Calculate Y-axis range to focus on holdings value fluctuations (excluding cash)
  const holdingsValues = chartData.data_points.map(point => point.total_value - point.cash_balance);
  const minValue = Math.min(...holdingsValues);
  const maxValue = Math.max(...holdingsValues);
  const range = maxValue - minValue;
  const padding = Math.max(range * 0.1, 10); // 10% padding or minimum $10

  const holdingsLayout = {
    title: { text: 'Holdings Value Over Time (7 Shares of AAPL)' },
    xaxis: { title: { text: 'Time' } },
    yaxis: {
      title: { text: 'Holdings Value ($)' },
      range: [minValue - padding, maxValue + padding],
      tickformat: '$.2f'
    },
    showlegend: false,
    height: 400,
    margin: { t: 50, r: 50, b: 50, l: 80 }
  };

  const pieLayout = {
    title: { text: 'Holdings Breakdown' },
    height: 400,
    margin: { t: 50, r: 50, b: 50, l: 50 }
  };

  const { performance_metrics } = chartData;
  const isPositive = performance_metrics.total_change >= 0;

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Performance Summary */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" display="flex" alignItems="center" gap={1}>
                  <Timeline />
                  Portfolio Performance
                </Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={timeRange}
                    label="Time Range"
                    onChange={handleTimeRangeChange}
                  >
                    <MenuItem value={1}>1 Day</MenuItem>
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                    <MenuItem value={90}>90 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="textSecondary">
                      Period Change
                    </Typography>
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      {isPositive ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                      <Typography 
                        variant="h6" 
                        color={isPositive ? 'success.main' : 'error.main'}
                      >
                        ${performance_metrics.total_change.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="textSecondary">
                      Percentage Change
                    </Typography>
                    <Typography 
                      variant="h6" 
                      color={isPositive ? 'success.main' : 'error.main'}
                    >
                      {performance_metrics.total_change_percent.toFixed(2)}%
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="textSecondary">
                      Data Points
                    </Typography>
                    <Typography variant="h6">
                      {performance_metrics.data_points_count}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="textSecondary">
                      Period
                    </Typography>
                    <Typography variant="h6">
                      {performance_metrics.period_days} Days
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Portfolio Value Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              {chartData.data_points.length > 0 ? (
                <Plot
                  data={[holdingsValueData]}
                  layout={holdingsLayout}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography variant="body1" color="textSecondary">
                    No historical data available. Creating initial snapshot...
                  </Typography>
                  <CircularProgress sx={{ mt: 2 }} />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Holdings Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              {chartData.holdings_breakdown.length > 0 ? (
                <Plot
                  data={[holdingsPieData]}
                  layout={pieLayout}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography variant="body1" color="textSecondary">
                    No holdings to display
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Holdings Details */}
        {chartData.holdings_breakdown.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Holdings Details
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  {chartData.holdings_breakdown.map((holding) => (
                    <Chip
                      key={holding.symbol}
                      label={`${holding.symbol}: $${holding.market_value.toFixed(2)} (${holding.percentage.toFixed(1)}%)`}
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default PortfolioChart;