from models import User, Fact, db
from app import app

db.drop_all()
db.create_all()


db.session.commit()
