import grpc
from concurrent import futures

import requests
import booking_pb2
import booking_pb2_grpc
import os
from database.models import db, Booking, Movie, Date
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
            self.db = Booking.query.options(joinedload(Booking.dates).joinedload(Date.movies)).all()
            
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
                                movieId=[movie.id for movie in date.movies]
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
                            movieId=[movie.id for movie in date.movies]
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

        with app.app_context():
            booking = Booking.query.filter_by(user_id=user_id).first()
            if booking:
                date = Date.query.filter_by(date=req_date).first()
                if date:
                    movie = Movie.query.filter_by(id=movie_id).first()
                    if movie:
                        date.movies.append(movie)
                        db.session.commit()
                        return booking_pb2.BookingData(
                            date=date.date,
                            movieId=[movie.id for movie in date.movies]
                        )
                    else:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"Movie with id {movie_id} not found")
                        return booking_pb2.BookingData()
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Date {req_date} not found")
                    return booking_pb2.BookingData()
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {user_id} not found")
                return booking_pb2.BookingData()
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    print("Server running in port 3003")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
