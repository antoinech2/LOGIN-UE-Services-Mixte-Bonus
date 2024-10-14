
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { Typography, List, ListItem } from '@mui/material';
import formatDate from '../helper/formatDate';
import IconButton from '@mui/material/IconButton';
import InfoIcon from '@mui/icons-material/Info';

import MovieDetails from '../components/MovieDetails';

export default function Bookings({date}) {

    const [bookings, setBookings] = useState([]);
    const [selectedMovie, setSelectedMovie] = useState(null);

    useEffect(() => {
        axios.get(`http://localhost:3004/available_bookings?date=${date}`)
            .then(response => setBookings(response.data))
            .catch(error => console.error(error));
    }, [date]);

    return (
        <>
            <Card
            sx={{
                minWidth: 275,
                maxWidth: 500,
                margin: 2,
                padding: 2
            }}>
                <CardContent>
                    <Typography variant="h5">Available bookings for {formatDate(date)}</Typography>
                    <List>
                        {bookings.map((booking, id) => (
                            <ListItem key={id}
                                secondaryAction={
                                    <IconButton edge="end" aria-label="delete" onClick={() => {setSelectedMovie(booking)}}>
                                        <InfoIcon />
                                    </IconButton>
                                }>
                                <Typography>
                                    {booking}
                                </Typography>
                            </ListItem>
                        ))}
                    </List>
                </CardContent>
            </Card>
            {selectedMovie && <MovieDetails name={selectedMovie} date={date}/>}
        </>
    );
}