#!/bin/bash

echo "Lancement des microservices..."

# Lancer chaque microservice en arrière-plan
python booking/booking.py &
echo "Microservice booking demarre"

python movie/movie.py &
echo "Microservice movie demarre"

python showtime/showtime.py &
echo "Microservice showtime demarre"

python user/user.py &
echo "Microservice user demarre"

# Attendre pour éviter que le script ne se termine immédiatement
echo "Appuyez sur Ctrl+C pour arrêter tous les microservices."
wait
