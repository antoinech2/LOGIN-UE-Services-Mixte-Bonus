import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Box } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Register() {
  const [name, setName] = useState('');
  const [userId, setUserId] = useState('');
  const [nameError, setNameError] = useState('');
  const [userIdError, setUserIdError] = useState('');
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const navigate = useNavigate();

  const validate = () => {
    let valid = true;

    if (name.trim() === '') {
      setNameError('Name is required');
      valid = false;
    } else {
      setNameError('');
    }

    if (userId.trim() === '') {
      setUserIdError('User ID is required');
      valid = false;
    } else {
      setUserIdError('');
    }

    return valid;
  };

  const handleRegister = async () => {
    if (validate()) {
      try {
        const response = await axios.post('http://localhost:3004/users', {
          name,
          id: userId,
        });

        if (response.status === 201) {
          setSuccessMessage('User registered successfully!');
          setServerError('');
          setName('');
          setUserId('');
          navigate('/bookings');
        } 
        } catch (error) {
            if (error.response.status === 409) {
            console.log("on a bien le 409");
            setServerError('User ID already exists. Please try another.');
        }
            else {
                console.log("on a bien le 500");
                setServerError('Failed to register. Please try again.');
        }
        }
      }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Box
        sx={{
          boxShadow: 3,
          padding: 4,
          borderRadius: 2,
          backgroundColor: '#f9f9f9',
        }}
      >
        <Typography variant="h4" gutterBottom align="center">
          Register
        </Typography>
        <TextField
          label="Name"
          variant="outlined"
          fullWidth
          margin="normal"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={Boolean(nameError)}
          helperText={nameError}
        />
        <TextField
          label="User ID"
          variant="outlined"
          fullWidth
          margin="normal"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          error={Boolean(userIdError)}
          helperText={userIdError}
        />

        {serverError && (
          <Typography variant="body2" color="error" align="center">
            {serverError}
          </Typography>
        )}

        {successMessage && (
          <Typography variant="body2" color="success" align="center">
            {successMessage}
          </Typography>
        )}

        <Button
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 3 }}
          onClick={handleRegister}
        >
          Register
        </Button>
      </Box>
    </Container>
  );
}
