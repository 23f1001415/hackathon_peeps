from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
import os
import logging

# Import models
from models import db, User, Event, Interest, Notification, EventCategory

# Import routes
from routes.auth import auth_bp
from routes.events import events_bp
from routes.interests import interests_bp
from routes.admin import admin_bp

# Import services
from services.notification import init_notification_service, schedule_event_reminders, mail
from services.geocoding import geocoding_service

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    if test_config is None:
        # Load configuration from environment variables or config files
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///community_pulse.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
            JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
            
            # Mail configuration
            MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
            MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
            MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'True') == 'True',
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME', ''),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', ''),
            MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@communitypulse.com'),
            
            # Geocoding configuration
            GEOCODING_API_KEY=os.environ.get('GEOCODING_API_KEY', ''),
            
            # Task scheduler settings
            SCHEDULER_API_ENABLED=True
        )
    else:
        # Load test configuration
        app.config.from_mapping(test_config)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app)
    
    # Initialize services
    init_notification_service(app)
    geocoding_service.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(interests_bp, url_prefix='/api/interests') 
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "Welcome to Community Pulse API!",
            "version": "1.0.0",
            "endpoints": {
                "authentication": "/api/auth",
                "events": "/api/events",
                "interests": "/api/interests",
                "admin": "/api/admin"
            }
        })
    
    # Setup scheduler for recurring tasks
    with app.app_context():
        try:
            scheduler = BackgroundScheduler()
            
            # Schedule event reminders daily at midnight
            scheduler.add_job(
                func=schedule_event_reminders,
                trigger='cron',
                hour=0,
                minute=0,
                id='event_reminders_job'
            )
            
            # Start the scheduler
            scheduler.start()
            app.logger.info("Background scheduler started")
        except Exception as e:
            app.logger.error(f"Error starting background scheduler: {e}")
    
    return app

def init_db():
    """Initialize the database with some sample data"""
    with create_app().app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have an admin user
        admin = User.query.filter_by(email='admin@communitypulse.com').first()
        if not admin:
            # Create admin user
            from werkzeug.security import generate_password_hash
            admin = User(
                name='Admin',
                email='admin@communitypulse.com',
                phone='1234567890',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_verified=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)