from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column('id', db.Integer, primary_key=True)
    fname = db.Column('fname', db.String(200))
    lname = db.Column('lname', db.String(200))
    uname = db.Column('uname', db.String(200), unique=True, nullable=False)
    password = db.Column('password', db.LargeBinary(60))
    createdAt = db.Column('createdTime', db.DateTime(timezone=True), default=func.now())
    lastUpdated = db.Column('updatedTime', db.DateTime(timezone=True), default=func.now())

class Pic(db.Model,UserMixin):
    __tablename__ = "pic"
    id = db.Column('id', db.Integer, primary_key=True)
    fname = db.Column('fname', db.String(200))
    lname = db.Column('lname', db.String(200))
    uname = db.Column('uname', db.String(200), unique=True, nullable=False)
    createdAt = db.Column('createdTime', db.DateTime(timezone=True), default=func.now())
    lastUpdated = db.Column('updatedTime', db.DateTime(timezone=True), default=func.now())
    profile = db.Column('profile', db.String(200))
