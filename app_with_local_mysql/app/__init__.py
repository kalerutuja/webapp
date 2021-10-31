from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Base = declarative_base()
# engine = create_engine('mysql://rutuja:rutuja123@localhost')
# engine.execute("CREATE DATABASE IF NOT EXISTS webapp")  # create db
# engine.execute("USE webapp")  # select new db
db = SQLAlchemy()
webapp = Flask(__name__)


def create_app():
    webapp.config['SECRET_KEY'] = 'gjasdgasgdghjdjsdgksj856876s5s7d57asd55'
    # application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csye6225:csye6225@csye6225.c6b2oknmn4xd.us-east-1.rds.amazonaws.com/csye6225'
    webapp.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://csye6225:csye6225@csye6225.c6b2oknmn4xd.us-east-1.rds.amazonaws.com/csye6225'
    webapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(webapp)
    from .auth import auth
    from .views import views

    webapp.register_blueprint(views, url_prefix='/')
    webapp.register_blueprint(auth, url_prefix='/')

    from .models import User

    return webapp

