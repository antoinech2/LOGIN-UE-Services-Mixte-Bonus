import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import os
from flask import Flask
from database.models import db, Movie, Schedule
from sqlalchemy.orm import joinedload

dirname = os.path.dirname(__file__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with app.app_context():
            self.schedules = Schedule.query.options(joinedload(Schedule.movies)).all()

    def Showtimes(self, request, context):
        print("Showtimes")
        with app.app_context():
            showtimes_data = showtime_pb2.ShowtimesData(
                showtimes=[
                    showtime_pb2.ShowtimeData(
                        date=schedule.date,
                        movies=[movie.id for movie in schedule.movies] 
                    ) for schedule in self.schedules
                ]
            )
            return showtimes_data

    def GetDates(self, request, context):
        print("GetDates")
        dates = [schedule.date for schedule in self.schedules]
        return showtime_pb2.DatesData(dates=dates)

    def GetMovieByDate(self, request, context):
        print("GetMovieByDate")
        date = request.date
        with app.app_context():
            schedule = Schedule.query.filter_by(date=date).first()
            if schedule:
                return showtime_pb2.ShowtimeData(
                    date=schedule.date,
                    movies=[movie.id for movie in schedule.movies]
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No movies found for the date: {date}")
                return showtime_pb2.ShowtimeData()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    print("Server running in port 3002")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
