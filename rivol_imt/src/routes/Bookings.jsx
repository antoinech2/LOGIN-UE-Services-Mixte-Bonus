import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { Container, Typography, Button, TextField, List, ListItem, Drawer, Box } from '@mui/material';
import formatDate from '../helper/formatDate';
import IconButton from '@mui/material/IconButton';
import InfoIcon from '@mui/icons-material/Info';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

import MovieDetails from '../components/MovieDetails';
import DateList from '../components/DateList';
import { Link } from 'react-router-dom';

export default function Bookings() {

    const [bookings, setBookings] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [userId, setUserId] = useState('');    
    const [loggedIn, setLoggedIn] = useState(false);
    const [userName, setUserName] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false); 
    const [userBookings, setUserBookings] = useState([]); 
    const [userError, setUserError] = useState(null);

    const handleLogin = () => {
      // request the server on port 3004 to check if the user exists
      axios.get(`http://localhost:3004/users/${userId}`)
        .then(response => {
          if (response.status === 200) {
            setUserName(response.data.name);
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

    const handleLogout = () => {
      setLoggedIn(false);
      setUserName(null);
      setUserId('');
      setMenuOpen(false);
      setUserBookings([]);
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
  
              // Use Promise.all to fetch movie titles for each movieId
              const bookingsWithMovieInfo = await Promise.all(
                  response.data.flatMap(async (booking) => {
                      // Map through each movieId for a booking
                      return await Promise.all(
                          booking.movieId.map(async (id) => {
                              const movieResponse = await axios.get(`http://localhost:3004/movie_info?id=${id}`);
                              // Return an object in {date, title} format for each movieId
                              return {
                                  date: booking.date,
                                  title: movieResponse.data.title // Extract the title
                              };
                          })
                      );
                  })
              );
  
              // Flatten the array and log the result
              const flattenedBookings = bookingsWithMovieInfo.flat();
              console.log("bookingsWithMovieInfo: ", flattenedBookings);
  
              // Update the state with enriched booking data in {date, title} format
              setUserBookings(flattenedBookings);
          } catch (error) {
              console.error(error);
              setUserBookings([]); // Set an empty list in case of error
          }
      };
  
      fetchUserBookings();
  }, [userId]);
  
  

    return (
        <>
          <Container>
            {!loggedIn ? (
              <>
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  justifyContent="center"
                  minHeight="100vh"
                  sx={{ backgroundColor: '#f0f0f0', padding: 4 }}
                >
                  <Box
                    sx={{
                      boxShadow: 3,
                      padding: 4,
                      borderRadius: 2,
                      backgroundColor: '#fff',
                      maxWidth: '400px',
                      width: '100%',
                    }}
                  >
                    <Typography variant="h4" gutterBottom align="center">
                      Login
                    </Typography>

                    <TextField
                      label="Enter User ID"
                      variant="outlined"
                      value={userId}
                      onChange={(e) => setUserId(e.target.value)}
                      fullWidth
                      margin="normal"
                    />

                    {userError ? (
                      <Box mt={2} mb={2}>
                        <Typography variant="body1" color="error">
                          User not found
                        </Typography>
                      </Box>
                    ) : null}

                    <Button
                      variant="outlined"
                      color="secondary"
                      fullWidth
                      component={Link}
                      to="/register"
                      sx={{ marginTop: 1 }}
                    >
                      New on this site? Create your account
                    </Button>

                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      onClick={handleLogin}
                      sx={{ marginTop: 3 }}
                    >
                      Login
                    </Button>
                  </Box>
                </Box>
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
                  <MovieDetails name={selectedMovie} date={selectedDate} user={userId}/>
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
                      Welcome {userName}
                    </Typography>
                    <Card>
                      <Typography variant="h5" color='info' paddingLeft={1}>
                        Your bookings
                      </Typography>
                      <List>
                        {userBookings.length > 0 ? (
                          userBookings.map((booking, index) => (
                            <ListItem button key={index}>
                              {formatDate(booking.date)} : {booking.title}
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
                  <Button
                    variant="contained"
                    color="error"
                    fullWidth
                    onClick={handleLogout}
                    sx={{ marginTop: 2, padding: 2 }}
                  >
                    Logout
                  </Button>
                </Drawer>
              </>
            )}
          </Container>
        </>
      );      
}
