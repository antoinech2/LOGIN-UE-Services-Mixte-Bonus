from flask import Flask
import json
from models import db, Booking
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
            for date_data in booking_data['dates']:
                for movie_id in date_data['movies']:
                    # Create a new booking
                    booking = Booking(user_id=booking_data['userid'], date=date_data['date'], movie_id=movie_id)
                    db.session.add(booking)
                    # Commit the changes after adding a new booking
                    db.session.commit()
                    
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
            print(booking.user_id, booking.movie_id, booking.date)

