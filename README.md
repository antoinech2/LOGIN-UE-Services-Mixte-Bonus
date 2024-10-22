# UE Services

## TP API BONUS (REST, GraphQL, gRPC + Front interface)

### IMT Atlantique Nantes - TAF LOGIN*

#### Nathan CLAEYS, Jean-Baptiste LAMBERTIN, Antoine CHEUCLE

## Projet description

The aim of this project is to illustrate the usage of different APIs between multiple microservices.
This project is a simulation of a cinema management application (simplified). There are 4 interacting microservices:

- **movie**, which manages data on films being shown
- **showtime**, which manages data on film release dates
- **booking**, manages users' viewing reservations
- **user**, provides an API that can be used by the service's customers.

In addition to previous TP, we improved the application with :

- New endpoints to interact with users and bookings
- Data migrated to SQL databases
- A front-end interface in React to use the service

In this TP, all internal services use REST to communicate, whereas the `user` service provides a REST API for the end-user.
All APIs documentation can be found in OpenAPI YAML file in the root of each service, or in GraphQL/gRPC schemas.

## How to run

### Requirements

- Python 3
- Node.js

- Install python modules (in `requirements.txt`)
- Install node modules (`npm install` in folder `/rivol_imt`)

### Project setup

To setup the project (initialize database and install Node dependencies), run file `init.sh`

### Automatic start (Windows and Linux)

To run all services automatically, simply run `run.bat` or `run.sh` at the root of the project.
Close the terminal to stop services

### Manual start

Run individually all services:

- `python movie/movie.py`
- `python showtime/showtime.py`
- `python booking/booking.py`
- `python user/user.py`
- `npm start` in folder `/rivol_imt` (for frontend)

### Additional information

Front-end development server runs on port 3010 and should be accessible on http://localhost:3010
