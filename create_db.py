# from hello import app, db
from app import app, db

# Creating an application context
with app.app_context():
    # Creating the database tables
    db.create_all()
