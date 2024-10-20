import React from 'react';
import { Typography, Container, Button } from '@mui/material';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <Container style={{ textAlign: 'center', marginTop: '50px' }}>
      <Typography variant="h3" gutterBottom>
        Welcome to the Rivol'IMT Booking System
      </Typography>
      <Typography variant="body1" paragraph>
        This is the home page of our application. You can navigate to the bookings page to view or manage your bookings.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        component={Link}
        to="/bookings"
        style={{ marginTop: '20px' }}
      >
        Go to Bookings
      </Button>
      <Typography variant="body1" paragraph style={{ marginTop: '20px' }}>
        If you are new to this site, please register to create an account.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        component={Link}
        to="/register"
        style={{ marginTop: '20px' }}>Click here to register</Button>
    </Container>
  );
}
