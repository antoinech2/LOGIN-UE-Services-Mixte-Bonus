from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

actor_film_association = db.Table('actor_film',
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id')),
    db.Column('film_id', db.Integer, db.ForeignKey('movies.id'))
)

class Actor(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.String(36), primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    birthyear = db.Column(db.Integer, nullable=False)
    films = db.relationship('Movie', secondary = actor_film_association)

    def __repr__(self):
        return f'<Actor {self.firstname} {self.lastname}>'

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    director = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Movie {self.title}>'
