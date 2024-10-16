
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { Container, Typography, Button, TextField, List, ListItem } from '@mui/material';
import formatDate from '../helper/formatDate';
import IconButton from '@mui/material/IconButton';
import InfoIcon from '@mui/icons-material/Info';

import MovieDetails from '../components/MovieDetails';
import DateList from '../components/DateList';

export default function Bookings() {

    const [bookings, setBookings] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [userId, setUserId] = useState('');    
    const [loggedIn, setLoggedIn] = useState(false);

    const handleLogin = () => {
        if (userId) {
          setLoggedIn(true); // Simuler la connexion avec un ID utilisateur
        }
      };

    useEffect(() => {
        setSelectedMovie(null);
        axios.get(`http://localhost:3004/available_bookings?date=${selectedDate}`)
            .then(response => setBookings(response.data))
            .catch(error => console.error(error));
    }, [selectedDate]);

    return (
        <>
          <Container>
            {!loggedIn ? (
              <>
                <Typography variant="h4" gutterBottom>
                  Login
                </Typography>
                <TextField
                  label="Enter User ID"
                  variant="outlined"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  fullWidth
                />
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleLogin}
                  style={{ marginTop: '20px' }}
                >
                  Login
                </Button>
              </>
            ) : (
              <>
                <Card
                  sx={{
                    minWidth: 275,
                    margin: 2,
                    padding: 2,
                  }}
                >
                  <Typography variant="h4">Bookings</Typography>
                  <Typography variant="h6">
                    Select a date to see available bookings
                  </Typography>
                  <DateList selector={setSelectedDate} />
                </Card>
                {selectedDate && (
                  <Card
                    sx={{
                      minWidth: 275,
                      maxWidth: 500,
                      margin: 2,
                      padding: 2,
                    }}
                  >
                    <CardContent>
                      <Typography variant="h5">
                        Available bookings for {formatDate(selectedDate)}
                      </Typography>
                      <List>
                        {bookings.map((booking, id) => (
                          <ListItem
                            key={id}
                            secondaryAction={
                              <IconButton
                                edge="end"
                                aria-label="info"
                                onClick={() => setSelectedMovie(booking)}
                              >
                                <InfoIcon />
                              </IconButton>
                            }
                          >
                            <Typography>{booking}</Typography>
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                )}
                {selectedMovie && (
                  <MovieDetails name={selectedMovie} date={selectedDate} />
                )}
              </>
            )}
          </Container>
        </>
      );      
}