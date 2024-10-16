@echo off
echo Lancement des microservices...

:: Lancer chaque microservice dans la même fenêtre et en arrière-plan
start /b python booking\booking.py
echo Microservice booking demarre

start /b python movie\movie.py
echo Microservice movie demarre

start /b python showtime\showtime.py
echo Microservice showtime demarre

start /b python user\user.py
echo Microservice user demarre

:: Attendre pour éviter que la fenêtre ne se ferme immédiatement
echo Appuyez sur Ctrl+C pour arrêter tous les microservices.
pause > nul
