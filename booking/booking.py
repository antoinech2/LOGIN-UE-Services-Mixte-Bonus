import grpc
from concurrent import futures

import requests
import booking_pb2
import booking_pb2_grpc
import json

import showtime_pb2
import showtime_pb2_grpc

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]
            
    def GetAllBookings(self, request, context):
        return booking_pb2.BookingDatabase(bookingList=[
            booking_pb2.BookingList(
                userid=booking["userid"],
                booking=[
                    booking_pb2.BookingData(
                        date=booking["date"],
                        movieId=booking["movies"]
                    ) for booking in booking["dates"]
                ]
            ) for booking in self.db
        ])
    
    def GetBookingsByUser(self, request, context):
        for booking in self.db:
            if booking["userid"] == request.id:
                return booking_pb2.BookingList(userid=request.id, booking=[
                    booking_pb2.BookingData(
                        date=booking["date"],
                        movieId=booking["movies"]
                    ) for booking in booking["dates"]
                ])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"No booking found for user: {request.id}")
        return booking_pb2.BookingList()
        
    def AddBookingForUser(self, request, context):
        user_id = request.user
        req_date = request.date
        movie_id = request.movie

        if not req_date or not movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Missing date or movie ID.")
            return booking_pb2.BookingData()
                
        # Check if user already has this booking
        for booking in self.db:
            if booking["userid"] == user_id:
                for schedule in booking["dates"]:
                    if schedule["date"] == req_date and movie_id in schedule["movies"]:
                        context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                        context.set_details("Booking already exists for this user.")
                        return booking_pb2.BookingData()

        # Ask showtimes service for a list of movies for the date
        #service_request = requests.get(f"http://127.0.0.1:3202/showtimes/{req_date}")
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            movies = stub.GetMovieByDate(showtime_pb2.Date(date=req_date))
            movies_list = list(movies.movies)
            print(movies_list)
        channel.close()



        if movie_id not in movies_list:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Movie not available for the selected date.")
            return booking_pb2.BookingData()

        # Add the booking for the specific user
        booking_found = False
        for booking in self.db:
            if booking["userid"] == user_id:
                for date_entry in booking["dates"]:
                    if date_entry["date"] == req_date:
                        if movie_id not in date_entry["movies"]:
                            date_entry["movies"].append(movie_id)
                        booking_found = True
                        break
                if not booking_found:
                    booking["dates"].append({"date": req_date, "movies": [movie_id]})
                break
        else:
            # Create a new booking if the user doesn't have any booking yet
            new_booking = {
                "userid": user_id,
                "dates": [{"date": req_date, "movies": [movie_id]}]
            }
            self.db.append(new_booking)

        # Use the write function to save the updated bookings
        write(self.db)

        # Return a successful BookingData response
        return booking_pb2.BookingData(date=req_date, movieId=[movie_id])
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    print("Server running in port 3003")
    server.wait_for_termination()

def write(bookings):
    with open('{}/data/bookings.json'.format("."), "w") as f:
        json.dump({"bookings": bookings}, f, indent=4)

if __name__ == '__main__':
    serve()
