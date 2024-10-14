
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { Typography, CardActions, Button } from '@mui/material';

export default function MovieDetails({name, date}){
    const [movie, setMovie] = useState([]);
    const [bookingResult, setBookingResult] = useState(null);

    useEffect(() => {
        setBookingResult(null);
        axios.get(`http://localhost:3004/movie_info?title=${name}`)
            .then(response => setMovie(response.data))
            .catch(error => console.error(error));
    }, [name]);

    const bookMovie = () => {
        if (!bookingResult){
            axios.post('http://localhost:3004/bookings/peter_curley', {
                date, movieid: movie.id
            })
            .then(response => {
                if (response.status === 200) {
                    setBookingResult("ok");
                } else {
                    setBookingResult("error");
                }
            })
            .catch(error => {
                if (error.status === 409) {
                    setBookingResult("booked");
                } else {
                    setBookingResult("error");
                }
            });    
        }
    }

    const buttonColor = () => {
        switch(bookingResult){
            case "ok":
                return "success";
            case "booked":
                return "warning";
            case "error":
                return "error";
            default:
                return "primary";
        }
    }

    const buttonText = () => {
        switch(bookingResult){
            case "ok":
                return "Booked successfully";
            case "booked":
                return "Already booked";
            case "error":
                return "Error";
            default:
                return "Book";
        }
    }

    return(
        <Card
        sx={{
            minWidth: 275,
            maxWidth: 500,
            margin: 2,
            padding: 2
        }}>
            <Typography variant="h5">{movie.title}</Typography>
            <CardContent>
                
                <Typography variant="h6" fontWeight="fontWeightRegular">Director: {movie.director}</Typography>
                <Typography variant="h6" fontWeight="fontWeightRegular">Rating: {movie.rating}/10</Typography>
            </CardContent>
            <CardActions>
                <Button color={buttonColor()} variant='contained' onClick={bookMovie}>
                    {buttonText()}
                </Button>
            </CardActions>
        </Card>
    )
}