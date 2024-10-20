from flask import Flask
import json
from models import db, Movie, Schedule
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
            schedules_data = mock_data['schedule']

        for schedule in schedules_data:
            new_schedule = Schedule(date=schedule['date'])
            for movie in schedule['movies']:
                existing_movie = Movie.query.filter_by(id=movie).first()
                if not existing_movie:
                    existing_movie = Movie(id=movie)
                    db.session.add(existing_movie)
                new_schedule.movies.append(existing_movie)
            db.session.add(new_schedule)
            
        db.session.commit()
        print("Database populated.")
        
if __name__ == "__main__":
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'database.db')):
        os.remove(os.path.join(os.path.dirname(__file__), 'database.db'))
    
    create_tables()
    populate_db()
    
    with app.app_context():
        schedules = Schedule.query.all()
        print("Schedules:")
        for schedule in schedules:
            print(schedule.date, schedule.movies)
        
        movies = Movie.query.all()
        print("Movies:")
        for movie in movies:
            print(movie.id)