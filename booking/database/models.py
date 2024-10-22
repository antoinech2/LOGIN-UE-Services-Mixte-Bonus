from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table linking booking, movie, and date
booking_movie_date_association = db.Table('booking_movie_date',
    db.Column('booking_id', db.Integer, db.ForeignKey('booking.id')),
    db.Column('movie_id', db.String(36), db.ForeignKey('movie.id')),
    db.Column('date_id', db.Integer, db.ForeignKey('date.id'))
)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.String(36), primary_key=True)

class Date(db.Model):
    __tablename__ = 'date'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(8), nullable=False)
    movies = db.relationship('Movie', secondary=booking_movie_date_association, backref='dates')

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), nullable=False)
    movies = db.relationship('Movie', secondary=booking_movie_date_association, backref='bookings')
    dates = db.relationship('Date', secondary=booking_movie_date_association, backref='bookings')
