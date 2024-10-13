import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json

class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    # write the code for the rpc call

    def Showtimes(self, request, context):
        print("Showtimes")
        showtimes_data = showtime_pb2.ShowtimesData(
            showtimes=[
                showtime_pb2.ShowtimeData(
                    date=showtime['date'],
                    movies=showtime['movies']
                ) for showtime in self.db
            ]
        )
        return showtimes_data
    
    def GetMovieByDate(self, request, context):
        date = request.date
        # Filter for the requested date
        movie = next((showtime for showtime in self.db if showtime["date"] == date), None)
        if movie:
            return showtime_pb2.ShowtimeData(
                date=movie["date"],
                movies=movie["movies"]
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
