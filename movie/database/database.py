from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from models import db, Actor, Movie
import os

# Initialize a separate Flask app for database handling
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables created.")

def populate_db():
    with app.app_context():
        with open(os.path.join(os.path.dirname(__file__), 'mock_data.json')) as f:
            mock_data = json.load(f)
            actors_data = mock_data['actors']
            movies_data = mock_data['movies']

        for movie in movies_data:
            new_movie = Movie(id=movie['id'], title=movie['title'], rating=movie['rating'], director=movie['director'])
            db.session.add(new_movie)

        for actor in actors_data:
            new_actor = Actor(id=actor['id'], firstname=actor['firstname'], lastname=actor['lastname'], birthyear=actor['birthyear'])
            for movie_id in actor['films']:
                movie = Movie.query.filter_by(id=movie_id).first()
                if movie:
                    new_actor.films.append(movie)
            
            db.session.add(new_actor)
            


        db.session.commit()
        print("Database populated.")

if __name__ == "__main__":
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'database.db')):
        os.remove(os.path.join(os.path.dirname(__file__), 'database.db'))
    
    create_tables()
    populate_db()
    
    with app.app_context():
        actors = Actor.query.all()
        print("Actors:")
        for actor in actors:
            print(actor.firstname, actor.lastname, actor.birthyear, actor.films)

        movies = Movie.query.all()
        print("Movies:")
        for movie in movies:
            print(movie.title, movie.rating, movie.director)
