from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

movie_date_association = db.Table('movie_date',
    db.Column('movie_id', db.String(36), db.ForeignKey('movie.id')),
    db.Column('date_id', db.Integer, db.ForeignKey('date.id'))
)

booking_date_association = db.Table('booking_date',
    db.Column('user_id', db.String(50), db.ForeignKey('booking.user_id')),
    db.Column('date_id', db.Integer, db.ForeignKey('date.id'))
)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.String(36), primary_key=True)

class Date(db.Model):
    __tablename__ = 'date'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(8), nullable=False)
    movies = db.relationship('Movie', secondary = movie_date_association)

class Booking(db.Model):
    __tablename__ = 'booking'
    user_id = db.Column(db.String(50), primary_key=True)
    dates = db.relationship('Date', secondary = booking_date_association)