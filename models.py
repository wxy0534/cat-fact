from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class Fact(db.Model):
    __tablename__ = 'facts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False, unique=True)
    # Include nullable to have each fact to be tied to a user
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False,
    )

    user = db.relationship('User')
        

class User(db.Model):
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False, unique=False)    
    
    facts = db.relationship('Fact')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.password}>"

    @classmethod
    def register(cls, username, pwd):
        hashed = bcrypt.generate_password_hash(pwd)       
        hashed_pwd = hashed.decode("UTF-8")        
        print(hashed_pwd)
        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
   
    @classmethod
    def authenticate(cls, username, pwd):    

        user = cls.query.filter_by(username=username).first()
        if user:
            print(user.password.encode('utf-8'))    
            print(pwd)
            is_auth = bcrypt.check_password_hash(user.password.encode('utf-8'), pwd)      
            if is_auth:
                return user
        else:
            return False




