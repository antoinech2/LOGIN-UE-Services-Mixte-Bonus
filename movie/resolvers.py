import json
import os

dirname = os.path.dirname(__file__)

def movie_with_id(_,info,_id):
    with open('{}/data/movies.json'.format(dirname), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie

def movie_with_title(_,info,_title):
    with open('{}/data/movies.json'.format(dirname), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['title'] == _title:
                return movie

def update_movie_rate(_,info,_id,_rate):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format(dirname), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format(dirname), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format(dirname), "r") as file:
        actors = json.load(file)
        result = [actor for actor in actors['actors'] if movie['id'] in actor['films']]
        return result