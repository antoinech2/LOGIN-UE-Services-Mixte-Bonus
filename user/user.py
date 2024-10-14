#Tkinter
import threading
import tkinter as tk

# REST API
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS, cross_origin
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
CORS(app)

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
    
    # We provide info to end-users (not the interal movie id)
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


def login():
    global var_userid
    var_userid = entry.get()  # Récupérer l'ID utilisateur
    if var_userid:  # Vérifie si un ID utilisateur a été entré
        root.destroy()  # Fermer la fenêtre actuelle et ouvrir l'interface principale
        start_tkinter_app()

# start flask app
def run_flask_app():
    app.run(host=HOST, port=PORT)

# start graphical interface
def start_tkinter_app():
    global listbox, entry, status_label, root, var_userid
    var_userid = var_userid if 'var_userid' in globals() else ""
    
    root = tk.Tk()

    if var_userid == "":  # Si aucun ID utilisateur, afficher l'écran de connexion
        root.title("Login")

        frame = tk.Frame(root)
        frame.pack(pady=20)

        entry_label = tk.Label(frame, text="Enter User ID:")
        entry_label.grid(row=0, column=0)
        entry = tk.Entry(frame)
        entry.grid(row=0, column=1)

        login_button = tk.Button(frame, text="Login", command=login)
        login_button.grid(row=0, column=2, padx=10)

    else:  # Une fois connecté, afficher l'interface principale
        root.title("Movies Showtime App")

        frame = tk.Frame(root)
        frame.pack(pady=20)

        entry_label = tk.Label(frame, text="Enter Date (YYYY-MM-DD):")
        entry_label.grid(row=0, column=0)
        entry = tk.Entry(frame)
        entry.grid(row=0, column=1)

        fetch_button = tk.Button(frame, text="Get Movies By Date")# , command=fetch_movies)
        fetch_button.grid(row=0, column=2, padx=10)

        listbox = tk.Listbox(root, width=50, height=10)
        listbox.pack(pady=10)

        all_showtimes_button = tk.Button(root, text="Get All Showtimes")#, command=fetch_showtimes)
        all_showtimes_button.pack(pady=10)

        status_label = tk.Label(root, text="", fg="red")
        status_label.pack()

    root.mainloop()


# Main code to run both Flask and Tkinter
if __name__ == "__main__":
    # start the Flask thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # start the Tkinter thread
    start_tkinter_app()

