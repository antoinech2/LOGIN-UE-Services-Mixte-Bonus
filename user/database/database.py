from flask import Flask
import json
from models import db, User
import os

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
            users_data = mock_data['users']

        for user in users_data:
            new_user = User(id=user['id'], name=user['name'], last_active=user['last_active'])
            db.session.add(new_user)
        
        db.session.commit()
        print("Database populated.")
        
if __name__ == "__main__":
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'database.db')):
        os.remove(os.path.join(os.path.dirname(__file__), 'database.db'))
    
    create_tables()
    populate_db()
    
    with app.app_context():
        users = User.query.all()
        print("Users:")
        for user in users:
            print(user.id, user.name, user.last_active)