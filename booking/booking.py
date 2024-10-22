import grpc
from concurrent import futures

import requests
import booking_pb2
import booking_pb2_grpc
import os
from database.models import db, Booking, Movie, Date, booking_movie_date_association
from sqlalchemy.orm import joinedload
from flask import Flask

import showtime_pb2
import showtime_pb2_grpc

dirname = os.path.dirname(__file__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with app.app_context():
            self.db = Booking.query.options(joinedload(Booking.movies).joinedload(Movie.dates)).all()
            
    def GetAllBookings(self, request, context):
        print("GetAllBookings")
        with app.app_context():
            booking_data = booking_pb2.BookingDatabase(
                bookingList=[
                    booking_pb2.BookingList(
                        userid=booking.user_id,
                        booking=[
                            booking_pb2.BookingData(
                                date=date.date,
                                movieId=[movie.id for movie in booking.movies if date in movie.dates]
                            ) for date in booking.dates
                        ]
                    ) for booking in self.db
                ]
            )
            return booking_data

    
    def GetBookingsByUser(self, request, context):
        print("GetBookingsByUser")
        user_id = request.id
        with app.app_context():
            booking = Booking.query.filter_by(user_id=user_id).first()
            if booking:
                return booking_pb2.BookingList(
                    userid=booking.user_id,
                    booking=[
                        booking_pb2.BookingData(
                            date=date.date,
                            movieId=[movie.id for movie in booking.movies if date in movie.dates]
                        ) for date in booking.dates
                    ]
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No bookings found for the user: {user_id}")
                return booking_pb2.BookingList()
        
    def AddBookingForUser(self, request, context):
        user_id = request.user
        req_date = request.date
        movie_id = request.movie

        if not req_date or not movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Missing date or movie ID.")
            return booking_pb2.BookingData()

        with app.app_context():
            # Check if the user already has a booking for this movie and date
            booking = Booking.query.filter_by(user_id=user_id).first()
            if booking and any(d.date == req_date and movie_id in [m.id for m in booking.movies if d in m.dates] for d in booking.dates):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f"Booking already exists for user {user_id}")
                return booking_pb2.BookingData()

            # Ask the showtimes service for available movies for the selected date
            with grpc.insecure_channel('localhost:3002') as channel:
                stub = showtime_pb2_grpc.ShowtimeStub(channel)
                movies = stub.GetMovieByDate(showtime_pb2.Date(date=req_date))
                movies_list = list(movies.movies)
            channel.close()

            # Check if the requested movie is available on the selected date
            if movie_id not in movies_list:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Movie not available for the selected date.")
                return booking_pb2.BookingData()

            # Create a new booking entry if the user has no existing booking
            if not booking:
                booking = Booking(user_id=user_id)
                db.session.add(booking)

            # Check if the date already exists in the Date table, otherwise create it
            date_entry = Date.query.filter_by(date=req_date).first()
            if not date_entry:
                date_entry = Date(date=req_date)
                db.session.add(date_entry)

            # Check if the movie already exists in the Movie table, otherwise create it
            movie_entry = Movie.query.filter_by(id=movie_id).first()
            if not movie_entry:
                movie_entry = Movie(id=movie_id)
                db.session.add(movie_entry)

            # Add the movie and date to the user's booking
            if movie_entry not in booking.movies:
                booking.movies.append(movie_entry)

            if date_entry not in booking.dates:
                booking.dates.append(date_entry)

            # Also ensure the association between the movie and the date
            if date_entry not in movie_entry.dates:
                movie_entry.dates.append(date_entry)

            # Commit the changes to the database
            db.session.commit()

            # Return the booking details as a response
            return booking_pb2.BookingData(date=req_date, movieId=[movie_id])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    print("Server running in port 3003")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
