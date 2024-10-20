from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_active = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<User {self.id}>'