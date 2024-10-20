import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { Container, Typography, Button, TextField, List, ListItem, Drawer } from '@mui/material';
import formatDate from '../helper/formatDate';
import IconButton from '@mui/material/IconButton';
import InfoIcon from '@mui/icons-material/Info';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

import MovieDetails from '../components/MovieDetails';
import DateList from '../components/DateList';

export default function Bookings() {

    const [bookings, setBookings] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [userId, setUserId] = useState('');    
    const [loggedIn, setLoggedIn] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false); 
    const [userBookings, setUserBookings] = useState([]); 
    const [userError, setUserError] = useState(null);

    const handleLogin = () => {
      // request the server on port 3004 to check if the user exists
      axios.get(`http://localhost:3004/users/${userId}`)
        .then(response => {
          if (response.status === 200) {
            setLoggedIn(true);
            setUserError(false);
          }
        })
        .catch(error => {
          if (error.response && error.response.status === 404) {
            // User not found
            setUserError(true); // Set the error state
          } else {
            console.error(error);
          }
        });
    };
    

    useEffect(() => {
        setSelectedMovie(null);
        if (selectedDate) {
          axios.get(`http://localhost:3004/available_bookings?date=${selectedDate}`)
              .then(response => setBookings(response.data))
              .catch(error => console.error(error));
        }
    }, [selectedDate]);

    useEffect(() => {
      const fetchUserBookings = async () => {
          try {
              const response = await axios.get(`http://localhost:3004/bookings/${userId}`);
              
              // Utilisation de Promise.all pour gérer les requêtes asynchrones dans map
              const bookingsWithMovieInfo = await Promise.all(
                  response.data.map(async (booking) => {
                      const movieResponse = await axios.get(`http://localhost:3004/movie_info?id=${booking.movieId}`);
                      return {
                          date: booking.date,
                          movie: movieResponse.data // Assigne le nom ou les infos du film ici
                      };
                  })
              );
  
              setUserBookings(bookingsWithMovieInfo); // Met à jour avec la liste enrichie
          } catch (error) {
              console.error(error);
              setUserBookings([]); // Liste vide en cas d'erreur
          }
      };
      fetchUserBookings();
  }, [userId]);
  

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
                {userError ? (<Typography variant="body1" color="error">User not found</Typography>) : null}
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
                
                <IconButton
                  edge="end"
                  aria-label="menu"
                  onClick={() => setMenuOpen(true)}
                  style={{ position: 'absolute', right: 20, top: 20 }}
                  size='large'
                >
                  <AccountBoxIcon /> 
                </IconButton>

                <Drawer
                  anchor="right"
                  open={menuOpen}
                  onClose={() => setMenuOpen(false)}
                >
                  <div style={{ width: 250, padding: 0 }}>
                    <Typography variant="h4" align='center' color='textPrimary'>
                      Welcome {userId}
                    </Typography>
                    <Card>
                      <Typography variant="h5" color='info' paddingLeft={1}>
                        Your bookings
                      </Typography>
                      <List>
                        {userBookings.length > 0 ? (
                          userBookings.map((booking, index) => (
                            <ListItem button key={index}>
                              {formatDate(booking.date)} : {booking.movie.title}
                            </ListItem>
                          ))
                        ) : (
                          <Typography variant="body1" color="textSecondary" align="center">
                            You have no booking yet
                          </Typography>
                        )}
                      </List>
                    </Card>
                  </div>
                </Drawer>
              </>
            )}
          </Container>
        </>
      );      
}
