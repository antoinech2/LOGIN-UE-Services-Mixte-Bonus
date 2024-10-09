# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc


app = Flask(__name__)
# Configurer les canaux gRPC vers les services Booking et Showtime
booking_channel = grpc.insecure_channel('localhost:3003')
booking_stub = booking_pb2_grpc.BookingStub(booking_channel)

showtime_channel = grpc.insecure_channel('localhost:3002')
showtime_stub = showtime_pb2_grpc.ShowtimeStub(showtime_channel)


PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def getUser(userid):
   for user in users:
      if user["id"] == userid:
         return user
   return None

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_users():
   return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_by_userid(userid):
   user = getUser(userid)
   if user:
      return make_response(jsonify(user), 200)
   return make_response(jsonify({"error":"User not found"}), 404)

@app.route("/movie_info", methods=['GET'])
def get_movie_info():
    if not "title" in request.args or not request.args["title"]:
       return make_response(jsonify({"error":"No title provided"}), 400)

    title = request.args["title"]


    url = 'http://127.0.0.1:3001/graphql'
    headers = {
        'Content-Type': 'application/json',
    }

    graphql_query = """
    query Movie_with_title {
        movie_with_title(_title: "The Good Dinosaur") {
            id
            title
            director
            rating
        }
    }
    """
    
    response = requests.post(url, json={'query': graphql_query}, headers=headers)
    # check if there is an error using the response code
    if not response.ok:
        if response.status_code == 404:
            return make_response(jsonify({"error":"No movie found"}), 404)
        return make_response(jsonify({"error":"Error in movie service"}), 500)
   
    # We provide info to end-users (not the interal movie id)
    response_json = response.json()
    movie = response_json["data"]["movie_with_title"]
    result = {
        "title": movie["title"],
        "director": movie["director"],
        "rating": movie["rating"],
        "id": movie["id"]
    }

    return make_response(jsonify(result), 200)

# Display movies that are available for booking on a specific date
@app.route("/available_bookings", methods=['GET'])
def get_available_bookings():
   # check if there is a date in the request
   if not "date" in request.args or not request.args["date"]:
      return make_response(jsonify({"error":"No date provided"}), 400)

   date = request.args["date"]

   # ask showtimes service a list of movies for the date
   date_request = showtime_pb2.Date(date=date)
   try:
      response = showtime_stub.GetMovieByDate(date_request)
      movies_id = response.movies
   except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.NOT_FOUND:
         return make_response(jsonify({"error": "No showtimes available for this date"}), 404)
      return make_response(jsonify({"error": "Error in showtimes service"}), 500)

   # get the name of the movies
   movies_name = []
   for movie in movies_id:
      movie_name = requests.get(f"http://127.0.0.1:3200/movies/{movie}/title")
      if not movie_name.ok:
         return make_response(jsonify({"error":"Error in movies service or unknown movie"}), 500)
      movies_name.append(movie_name.text)

   return make_response(jsonify(movies_name), 200)

# Add a booking for a movie
@app.route("/bookings/<userid>", methods=['POST'])
def create_booking_by_userid(userid):
   req = request.get_json()
   date = req.get("date")
   movie = req.get("movieid")
   
   if not getUser(userid):
      return make_response(jsonify({"error":"User not found"}), 404)

   # Préparation de la requête gRPC pour ajouter une réservation
   booking_request = booking_pb2.AddBookingRequest(user=userid, date=date, movie=movie)

   try:
      response = booking_stub.AddBookingForUser(booking_request)
      return make_response(jsonify({"date": response.date, "movieId": list(response.movieId)}), 200)
   except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
         return make_response(jsonify({"error": "Missing date or movie ID"}), 400)
      elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
         return make_response(jsonify({"error": "Booking already exists for this user"}), 409)
      return make_response(jsonify({"error": "Error in booking service"}), 500)

# Get bookings of a user
@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
   user_request = booking_pb2.User(id=userid)

   try:
      response = booking_stub.GetBookingsByUser(user_request)
      bookings = [{"userid": userid, "date": booking.date, "movieId": list(booking.movieId)} for booking in response.booking]
      return make_response(jsonify(bookings), 200)
   except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.NOT_FOUND:
         return make_response(jsonify({"error": "Invalid user ID"}), 404)
      return make_response(jsonify({"error": "Error in service booking"}), 500)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
