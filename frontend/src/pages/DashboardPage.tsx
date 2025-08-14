import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  MenuBook,
  Group,
  SwapHoriz,
  Message,
  TrendingUp,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { Book } from '../types';
import apiService from '../services/api';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [recentBooks, setRecentBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const books = await apiService.getBooks();
        setRecentBooks(books.slice(0, 6)); // Show only first 6 books
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const statsCards = [
    {
      title: 'My Books',
      value: '42',
      icon: <MenuBook />,
      color: '#1976d2',
    },
    {
      title: 'Friends',
      value: '18',
      icon: <Group />,
      color: '#388e3c',
    },
    {
      title: 'Active Exchanges',
      value: '3',
      icon: <SwapHoriz />,
      color: '#f57c00',
    },
    {
      title: 'Messages',
      value: '7',
      icon: <Message />,
      color: '#7b1fa2',
    },
  ];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 4 }}>
        Welcome back, {user?.first_name}!
      </Typography>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                background: `linear-gradient(135deg, ${stat.color}22, ${stat.color}11)`,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: stat.color,
                    color: 'white',
                    mr: 2,
                  }}
                >
                  {stat.icon}
                </Box>
                <Typography component="h2" variant="h6" color="text.secondary">
                  {stat.title}
                </Typography>
              </Box>
              <Typography component="p" variant="h4" sx={{ color: stat.color }}>
                {stat.value}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Books in the Network
            </Typography>
            <Grid container spacing={2}>
              {recentBooks.map((book) => (
                <Grid item xs={12} sm={6} key={book.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography gutterBottom variant="h6" component="div" noWrap>
                        {book.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        by {book.author_names}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {book.genres?.slice(0, 2).map((genre) => (
                          <Chip key={genre.id} label={genre.name} size="small" />
                        ))}
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button size="small">View Details</Button>
                      <Button size="small">Request Exchange</Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button variant="outlined" startIcon={<MenuBook />} fullWidth>
                Add a Book
              </Button>
              <Button variant="outlined" startIcon={<Group />} fullWidth>
                Find Friends
              </Button>
              <Button variant="outlined" startIcon={<SwapHoriz />} fullWidth>
                Browse Exchanges
              </Button>
              <Button variant="outlined" startIcon={<Message />} fullWidth>
                Send Message
              </Button>
            </Box>
          </Paper>

          {/* Activity Feed */}
          <Paper sx={{ p: 2 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Activity
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2">
                  Sarah requested to exchange "The Great Gatsby"
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Group sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2">
                  You have a new friend request from Mike
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Message sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="body2">
                  New message about "1984" discussion
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage; 