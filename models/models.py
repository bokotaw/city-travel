from .. import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(50))
    lat = db.Column(db.REAL)
    lng = db.Column(db.REAL)
    country = db.Column(db.String(50))
    iso2 = db.Column(db.String(10))
    admin_name = db.Column(db.String(50))
    capital = db.Column(db.String(50))
    population = db.Column(db.Integer)
    population_proper = db.Column(db.Integer)


class Visited(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    city_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    city_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)


class MyPlaces(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    country = db.Column(db.String(50))
    admin_name = db.Column(db.String(50))
    lat = db.Column(db.REAL)
    lng = db.Column(db.REAL)


