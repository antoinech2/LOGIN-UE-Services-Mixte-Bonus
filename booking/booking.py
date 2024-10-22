import grpc
from concurrent import futures

import booking_pb2
import booking_pb2_grpc
import os
from database.models import db, Booking
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
            self.db = Booking.query.all()
            
    def GetAllBookings(self, request, context):
        print("GetAllBookings")
        with app.app_context():
            booking_data = booking_pb2.BookingDatabase(
                bookingList=[
                    booking_pb2.BookingList(
                        userid=booking.user_id,
                        booking=[
                            booking_pb2.BookingData(
                                date=booking.date,
                                movieId=[booking.movie_id]
                            )
                        ]
                    ) for booking in self.db
                ]
            )
            return booking_data

    
    def GetBookingsByUser(self, request, context):
        print("GetBookingsByUser")
        user_id = request.id
        with app.app_context():
            bookings = Booking.query.filter_by(user_id=user_id).all()
            if bookings:
                return booking_pb2.BookingList(
                    userid=user_id,
                    booking=[
                        booking_pb2.BookingData(
                            date=booking.date,
                            movieId=[booking.movie_id]
                        ) for booking in bookings
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
            existing_booking = Booking.query.filter_by(user_id=user_id, date=req_date, movie_id=movie_id).first()
            if existing_booking:
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

            # Create a new booking entry
            new_booking = Booking(user_id=user_id, movie_id=movie_id, date=req_date)
            db.session.add(new_booking)
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
