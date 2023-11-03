# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'remix'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from routes import *
from models import *

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# if __name__ == '__main__':
#     app.run(debug=True)

