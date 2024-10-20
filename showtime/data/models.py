from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

schedule_movies_association = db.Table('schedule_movies',
    db.Column('movie_id', db.String(36), db.ForeignKey('movies.id')),
    db.Column('schedule_date', db.Integer, db.ForeignKey('schedules.date'))
)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.String(36), primary_key=True)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    date = db.Column(db.String(8), primary_key=True)
    movies = db.relationship('Movie', secondary = schedule_movies_association)