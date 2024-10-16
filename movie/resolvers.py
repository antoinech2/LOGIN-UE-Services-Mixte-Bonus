from sqlalchemy import inspect
from database.models import db, Movie, Actor
from flask import current_app

def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }

def movie_with_id(_,info,_id):
    with current_app.app_context():
        movie = db.session.query(Movie).filter_by(id=_id).first()
        return object_as_dict(movie)

def movie_with_title(_,info,_title):
    with current_app.app_context():
        movie = db.session.query(Movie).filter_by(title=_title).first()
        return object_as_dict(movie)

def update_movie_rate(_,info,_id,_rate):
    with current_app.app_context():
        movie = db.session.query(Movie).filter_by(id=_id).first()
        movie.rating = _rate
        db.session.commit()
        return object_as_dict(movie)

def resolve_actors_in_movie(movie, info):
    with current_app.app_context():
        actors = db.session.query(Actor).filter(Actor.films.any(id=movie['id'])).all()
        actors_list = []
        for actor in actors:
            actor_dict = object_as_dict(actor)
            actor_dict['films'] = [object_as_dict(film)["id"] for film in actor.films]
            actors_list.append(actor_dict)
        return actors_list
