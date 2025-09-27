from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -- USERS TABLE --
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # either 'admin' or 'user'
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    # One user can have many bookings
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

# -- PARKING LOT TABLE --
class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)

    # One lot has many parking spots
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)

    def __repr__(self):
        return f"<Lot {self.prime_location}>"

# -- PARKING SPOT TABLE --
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied

    # One spot can have at most one active booking
    booking = db.relationship('Booking', backref='spot', lazy=True, uselist=False)

    def __repr__(self):
        return f"<Spot {self.id} in Lot {self.lot_id}>"

# -- BOOKINGS TABLE --
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(15), nullable=False)

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)

    def __repr__(self):
        return f"<Booking #{self.id}>"
