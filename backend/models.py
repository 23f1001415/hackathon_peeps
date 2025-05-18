from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class EventCategory(enum.Enum):
    garage_sale = "Garage Sale"
    sports = "Sports Match"
    community_class = "Community Class"
    volunteer = "Volunteer Opportunity"
    exhibition = "Exhibition"
    festival = "Festival or Celebration"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))  # Add password field
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    events_created = db.relationship('Event', backref='creator', lazy=True, foreign_keys='Event.created_by')
    interests = db.relationship('Interest', backref='user_interest', lazy=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.Enum(EventCategory), nullable=False)
    location = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved = db.Column(db.Boolean, default=False)
    flagged = db.Column(db.Boolean, default=False)
    max_attendees = db.Column(db.Integer, nullable=True)
    interests = db.relationship('Interest', backref='event_interest', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    attendees = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to registered user if applicable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    """Model to track notifications sent to users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # reminder, update, cancellation
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, sent, failed
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    event = db.relationship('Event', backref='notifications')
    user = db.relationship('User', backref='notifications')