from flask import Flask
import json
from models import db, Movie, Date, Booking
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
            bookings_data = mock_data['bookings']

        for bookings in bookings_data:
            for date in bookings['dates']:
                for movie in date['movies']:
                    exists = Movie.query.filter_by(id=movie).first()
                    if exists:
                        continue
                    new_movie = Movie(id=movie)
                    db.session.add(new_movie)
                
            exists = Booking.query.filter_by(user_id=bookings['userid']).first()
            if exists:
                continue
            new_booking = Booking(user_id=bookings['userid'])
            for date in bookings['dates']:
                new_date = Date(date=date['date'])
                new_date.movies = [Movie.query.filter_by(id=movie).first() for movie in date['movies']]
                db.session.add(new_date)
                new_booking.dates.append(new_date)
                
            db.session.add(new_booking)
        db.session.commit()
        print("Database populated.")


if __name__ == "__main__":
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'database.db')):
        os.remove(os.path.join(os.path.dirname(__file__), 'database.db'))
    
    create_tables()
    populate_db()
    
    with app.app_context():
        bookings = Booking.query.all()
        print("Bookings:")
        for booking in bookings:
            print(booking.user_id, booking.dates)
        
        dates = Date.query.all()
        print("Dates:")
        for date in dates:
            print(date.date, date.movies)
        
        movies = Movie.query.all()
        print("Movies:")
        for movie in movies:
            print(movie.id)