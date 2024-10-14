
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Stack } from '@mui/material';
import formatDate from '../helper/formatDate';

export default function DateList({selector}){
    const [dates, setDates] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:3004/available_dates')
            .then(response => setDates(response.data))
            .catch(error => console.error(error));
    }, []);

    return(
        <Stack direction={'row'} spacing={2} margin={2}>
        {dates.map((date, id) => (
            <Button key={id} variant="contained" color="primary" onClick={() => {selector(date)}}>{formatDate(date)}</Button>
        ))}
        </Stack>
    )
}