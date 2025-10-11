import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Box,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  Security,
  Warning,
  TrendingUp,
  Public,
  Assessment
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface ThreatMetrics {
  total_threats: number;
  active_incidents: number;
  threat_categories: Record<string, number>;
  risk_levels: Record<string, number>;
  recent_activity: Array<{
    timestamp: string;
    type: string;
    severity: string;
    source: string;
    description: string;
  }>;
}

interface ThreatTrend {
  date: string;
  count: number;
  severity: Record<string, number>;
}

const COLORS = ['#f44336', '#ff9800', '#ffeb3b', '#4caf50'];
const SEVERITY_COLORS = {
  CRITICAL: '#d32f2f',
  HIGH: '#f57c00',
  MEDIUM: '#fbc02d',
  LOW: '#388e3c'
};

const ThreatDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<ThreatMetrics | null>(null);
  const [trends, setTrends] = useState<ThreatTrend[]>([]);
  const [threatMap, setThreatMap] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch dashboard metrics
      const metricsResponse = await fetch('/api/v1/dashboard/metrics');
      if (!metricsResponse.ok) throw new Error('Failed to fetch metrics');
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      // Fetch threat trends
      const trendsResponse = await fetch('/api/v1/analytics/trends');
      if (!trendsResponse.ok) throw new Error('Failed to fetch trends');
      const trendsData = await trendsResponse.json();
      setTrends(trendsData.daily_threats || []);

      // Fetch threat map
      const mapResponse = await fetch('/api/v1/dashboard/threat-map');
      if (!mapResponse.ok) throw new Error('Failed to fetch threat map');
      const mapData = await mapResponse.json();
      setThreatMap(mapData.threat_sources || []);

      setError(null);
    } catch (err: any) {
      setError(err.message);
      console.error('Dashboard fetch error:', err);

      // Mock data for demo
      setMetrics({
        total_threats: 1247,
        active_incidents: 23,
        threat_categories: {
          'APT36_TRANSPARENT_TRIBE': 45,
          'RANSOMWARE_DOUBLE_EXTORTION': 32,
          'PHISHING_SOCIAL_ENGINEERING': 78,
          'INSIDER_THREAT': 21,
          'API_ABUSE': 15
        },
        risk_levels: {
          'CRITICAL': 8,
          'HIGH': 15,
          'MEDIUM': 45,
          'LOW': 67
        },
        recent_activity: [
          {
            timestamp: new Date().toISOString(),
            type: 'APT36_TRANSPARENT_TRIBE',
            severity: 'HIGH',
            source: '203.0.113.100',
            description: 'APT36 credential harvesting detected'
          },
          {
            timestamp: new Date(Date.now() - 300000).toISOString(),
            type: 'RANSOMWARE_DOUBLE_EXTORTION', 
            severity: 'CRITICAL',
            source: '198.51.100.50',
            description: 'Ransomware encryption attempt blocked'
          }
        ]
      });

      setTrends([
        { date: '2025-10-01', count: 45, severity: { HIGH: 12, MEDIUM: 20, LOW: 13 } },
        { date: '2025-10-02', count: 38, severity: { HIGH: 8, MEDIUM: 18, LOW: 12 } },
        { date: '2025-10-03', count: 52, severity: { HIGH: 15, MEDIUM: 22, LOW: 15 } }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !metrics) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center">
          <Typography variant="h6" sx={{ mb: 2 }}>Loading Thales Cyber Shield Dashboard...</Typography>
          <LinearProgress sx={{ width: '50%' }} />
        </Box>
      </Container>
    );
  }

  const riskData = metrics ? Object.entries(metrics.risk_levels).map(([level, count]) => ({
    name: level,
    value: count,
    color: SEVERITY_COLORS[level as keyof typeof SEVERITY_COLORS]
  })) : [];

  return (
    <div>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Security sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Thales Cyber Shield - AI-Powered Threat Detection
          </Typography>
          <Chip 
            label="OPERATIONAL" 
            color="success" 
            variant="outlined"
            sx={{ color: 'white', borderColor: 'white' }}
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 4 }}>
        {error && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {error} - Showing demo data
          </Alert>
        )}

        {/* Key Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Warning color="error" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Threats
                    </Typography>
                    <Typography variant="h4">
                      {metrics?.total_threats.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Security color="warning" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Active Incidents
                    </Typography>
                    <Typography variant="h4">
                      {metrics?.active_incidents || '0'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <TrendingUp color="success" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Detection Rate
                    </Typography>
                    <Typography variant="h4">
                      98.5%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Public color="info" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Threat Sources
                    </Typography>
                    <Typography variant="h4">
                      {threatMap.length || '0'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Threat Trends Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader 
                title="Threat Trends (Last 30 Days)"
                avatar={<Assessment />}
              />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="count" stroke="#1976d2" fill="#1976d2" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Risk Levels Distribution */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Risk Distribution" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <Box sx={{ mt: 2 }}>
                  {riskData.map((entry) => (
                    <Box key={entry.name} display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Box display="flex" alignItems="center">
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            bgcolor: entry.color,
                            mr: 1
                          }}
                        />
                        <Typography variant="body2">{entry.name}</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="bold">{entry.value}</Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Threat Categories */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Top Threat Categories" />
              <CardContent>
                {metrics && Object.entries(metrics.threat_categories).slice(0, 5).map(([category, count]) => (
                  <Box key={category} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                      <Typography variant="body2" sx={{ fontSize: '0.9rem' }}>
                        {category.replace(/_/g, ' ')}
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">{count}</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min((count / Math.max(...Object.values(metrics.threat_categories))) * 100, 100)} 
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Recent Threat Activity" />
              <CardContent>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Time</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Source</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {metrics?.recent_activity.slice(0, 5).map((activity, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {new Date(activity.timestamp).toLocaleTimeString()}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                              {activity.type.replace(/_/g, ' ')}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={activity.severity} 
                              size="small"
                              sx={{
                                bgcolor: SEVERITY_COLORS[activity.severity as keyof typeof SEVERITY_COLORS],
                                color: 'white',
                                fontSize: '0.7rem'
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                              {activity.source}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Indian Threat Landscape */}
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Indian Threat Landscape - APT Groups Monitoring" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">APT36 (Transparent Tribe)</Typography>
                      <Typography variant="body2">
                        45 incidents detected | Pakistani origin | Targeting: Defense, Government
                      </Typography>
                    </Alert>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">SideCopy APT</Typography>
                      <Typography variant="body2">
                        32 incidents detected | Pakistani origin | Targeting: Military, Government  
                      </Typography>
                    </Alert>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">APT41 (Chinese)</Typography>
                      <Typography variant="body2">
                        28 incidents detected | Chinese origin | Targeting: Healthcare, Telecom
                      </Typography>
                    </Alert>
                  </Grid>
                </Grid>

                <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                  🇮🇳 India-Specific Threat Intelligence
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip label="CERT-In Integration" color="primary" size="small" />
                  <Chip label="12 Languages Supported" color="success" size="small" />
                  <Chip label="Government Sector Focus" color="warning" size="small" />
                  <Chip label="Banking Sector Protection" color="info" size="small" />
                  <Chip label="Critical Infrastructure" color="error" size="small" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
};

export default ThreatDashboard;
