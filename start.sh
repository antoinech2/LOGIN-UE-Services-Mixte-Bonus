#!/bin/bash
echo "Starting all microservices..."

# Function to kill all background processes when script is interrupted
cleanup() {
    echo "Stopping all microservices..."
    pkill -P $$  # Kills all child processes of this script
    exit 0
}

# Trap Ctrl+C (SIGINT) and call the cleanup function
trap cleanup SIGINT

# Start all microservices
python booking/booking.py &
echo "Booking microservice started"

python movie/movie.py &
echo "Movie microservice started"

python showtime/showtime.py &
echo "Showtime microservice started"

python user/user.py &
echo "User microservice started"

# Change directory to frontend and start the frontend
cd rivol_imt
npm start &
echo "Frontend started"

# Keep the script running to catch CTRL+C and manage background processes
echo "All microservices started. Press CTRL+C to stop all microservices"
wait