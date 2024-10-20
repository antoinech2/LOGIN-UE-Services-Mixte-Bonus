from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests
from werkzeug.exceptions import NotFound
import os
from database.models import db, User
from sqlalchemy import inspect

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc


app = Flask(__name__)
CORS(app)

dirname = os.path.dirname(__file__)

# Configurer les canaux gRPC vers les services Booking et Showtime
booking_channel = grpc.insecure_channel('localhost:3003')
booking_stub = booking_pb2_grpc.BookingStub(booking_channel)

showtime_channel = grpc.insecure_channel('localhost:3002')
showtime_stub = showtime_pb2_grpc.ShowtimeStub(showtime_channel)


PORT = 3004
HOST = '0.0.0.0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database/database.db')
app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def getUser(userid):
    user = db.session.query(User).filter(User.id == userid).first()
    return object_as_dict(user)

def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_users():
    users = db.session.query(User).all()
    users = [object_as_dict(user) for user in users]
    return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_by_userid(userid):
   user = getUser(userid)
   if user:
      return make_response(jsonify(user), 200)
   return make_response(jsonify({"error":"User not found"}), 404)

@app.route("/users", methods=['POST'])
def create_user():
   req = request.get_json()
   if not req or not "id" in req or not "name" in req:
      return make_response(jsonify({"error":"Missing id or name"}), 400)
   userid = req["id"]
   username = req["name"]
   if getUser(userid):
      return make_response(jsonify({"error":"User already exists"}), 409)
   users.append({"id": userid, "name": username, "last_active": 0})
   with open('{}/data/users.json'.format(dirname), "w") as jsf:
      json.dump({"users": users}, jsf , indent=4)
   return make_response(jsonify({"id": userid, "name": username}), 201)

@app.route("/movie_info", methods=['GET'])
def get_movie_info():
    url = 'http://127.0.0.1:3001/graphql'
    headers = {
        'Content-Type': 'application/json',
    }

    if "title" in request.args and request.args["title"]:
       title = request.args["title"]
       graphql_query = """
         query Movie_with_title {
            movie_with_title(_title: "%s") {
                  id
                  title
                  director
                  rating
            }
         }
         """%(title)
       graphql_data = requests.post(url, json={'query': graphql_query}, headers=headers)
    
       if graphql_data.status_code != 200:
         return make_response(jsonify({"error":"Error in movie service"}), 500)
       movie = graphql_data.json()["data"]["movie_with_title"]
       if not movie:
         return make_response(jsonify({"error":"No movie found"}), 404)
       
    elif "id" in request.args and request.args["id"]:
         id = request.args["id"]
         graphql_query = """
            query Movie_with_id {
               movie_with_id(_id: "%s") {
                     id
                     title
                     director
                     rating
               }
            }
            """%(id)
         graphql_data = requests.post(url, json={'query': graphql_query}, headers=headers)
         if graphql_data.status_code != 200:
            return make_response(jsonify({"error":"Error in movie service"}), 500)
         movie = graphql_data.json()["data"]["movie_with_id"]
         if not movie:
            return make_response(jsonify({"error":"No movie found"}), 404)           
    else:
         return make_response(jsonify({"error":"No title or id provided"}), 400)    
    
   
    
    # We provide info to end-users (not the interal movie id)
    result = {
        "title": movie["title"],
        "director": movie["director"],
        "rating": movie["rating"],
        "id": movie["id"]
    }

    return make_response(jsonify(result), 200)

@app.route("/available_dates", methods=['GET'])
def get_available_dates():
   # ask showtimes service for available dates
   try:
      response = showtime_stub.GetDates(showtime_pb2.Empty())
      dates = response.dates
      return make_response(jsonify(list(dates)), 200)
   except grpc.RpcError as e:
      return make_response(jsonify({"error": "Error in showtimes service"}), 500)

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
   for movie_id in movies_id:
      url = 'http://127.0.0.1:3001/graphql'
      headers = {
        'Content-Type': 'application/json',
      }
      graphql_query = """
      query Movie_with_id {
        movie_with_id(_id: "%s") {
            title
        }
      }
      """%(movie_id)
      graphql_data = requests.post(url, json={'query': graphql_query}, headers=headers)
      if graphql_data.status_code != 200:
         return make_response(jsonify({"error":"Error in movie service"}), 500)
      movie_name = graphql_data.json()["data"]["movie_with_id"]["title"]
      movies_name.append(movie_name)

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