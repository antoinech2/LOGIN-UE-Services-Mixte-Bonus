from flask import Flask
import json
from models import db, Movie, Date, Booking, booking_movie_date_association
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

        for booking_data in bookings_data:
            # Check if booking for this user already exists
            existing_booking = Booking.query.filter_by(user_id=booking_data['userid']).first()
            if not existing_booking:
                # Create a new booking
                new_booking = Booking(user_id=booking_data['userid'])
                db.session.add(new_booking)
                db.session.commit()  # Ensure booking_id is generated

            for date_data in booking_data['dates']:
                # Check if date exists
                existing_date = Date.query.filter_by(date=date_data['date']).first()
                if not existing_date:
                    existing_date = Date(date=date_data['date'])
                    db.session.add(existing_date)
                    db.session.commit()  # Ensure date_id is generated

                for movie_id in date_data['movies']:
                    # Check if movie exists
                    existing_movie = Movie.query.filter_by(id=movie_id).first()
                    if not existing_movie:
                        existing_movie = Movie(id=movie_id)
                        db.session.add(existing_movie)
                        db.session.commit()  # Ensure movie_id is generated

                    # Link movie, date, and booking in the many-to-many table
                    if existing_movie not in new_booking.movies:
                        new_booking.movies.append(existing_movie)

                    if existing_date not in new_booking.dates:
                        new_booking.dates.append(existing_date)

                    # Also ensure the association between the movie and the date
                    if existing_date not in existing_movie.dates:
                        existing_movie.dates.append(existing_date)

            # Commit all changes after linking movies, dates, and bookings
            db.session.commit()
        print("Database populated.")

if __name__ == "__main__":
    # Remove the existing database file if it exists
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    
    create_tables()
    populate_db()
    
    # Display the database contents
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
