# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
#import booking_pb2
#import booking_pb2_grpc
#import movie_pb2
#import movie_pb2_grpc

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_users():
   return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_by_userid(userid):
   for user in users:
      if user["id"] == userid:
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
    print(movie)
    result = {
        "title": movie["title"],
        "director": movie["director"],
        "rating": movie["rating"],
        "id": movie["id"]
    }

    return make_response(jsonify(result), 200)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
