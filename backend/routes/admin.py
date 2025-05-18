from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Event, Interest
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Admin role authorization decorator
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({"message": "Admin privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

@admin_bp.route('/events/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_events():
    events = Event.query.filter_by(approved=False).all()
    
    events_list = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'created_by': event.created_by,
        'creator_name': User.query.get(event.created_by).name if User.query.get(event.created_by) else 'Unknown',
        'created_at': event.created_at.isoformat()
    } for event in events]
    
    return jsonify(events_list)

@admin_bp.route('/events/<int:event_id>/approve', methods=['PATCH'])
@jwt_required()
@admin_required
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    event.approved = True
    event.flagged = False  # Clear any flags
    db.session.commit()
    
    # Here you would send a notification to the event creator
    
    return jsonify({"message": "Event approved successfully"})

@admin_bp.route('/events/<int:event_id>/reject', methods=['PATCH'])
@jwt_required()
@admin_required
def reject_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    event.approved = False
    db.session.commit()
    
    # Here you would send a notification to the event creator
    
    return jsonify({"message": "Event rejected successfully"})

@admin_bp.route('/events/<int:event_id>/flag', methods=['PATCH'])
@jwt_required()
@admin_required
def flag_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    event.flagged = True
    db.session.commit()
    
    return jsonify({"message": "Event flagged successfully"})

@admin_bp.route('/events/flagged', methods=['GET'])
@jwt_required()
@admin_required
def get_flagged_events():
    events = Event.query.filter_by(flagged=True).all()
    
    events_list = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'created_by': event.created_by,
        'creator_name': User.query.get(event.created_by).name if User.query.get(event.created_by) else 'Unknown',
        'approved': event.approved,
        'created_at': event.created_at.isoformat()
    } for event in events]
    
    return jsonify(events_list)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    
    users_list = [{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_verified': user.is_verified,
        'is_banned': user.is_banned
    } for user in users]
    
    return jsonify(users_list)

@admin_bp.route('/users/<int:user_id>/events', methods=['GET'])
@jwt_required()
@admin_required
def get_user_events(user_id):
    # Check if user exists
    user = User.query.get_or_404(user_id)
    
    events = Event.query.filter_by(created_by=user_id).all()
    
    events_list = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'approved': event.approved,
        'flagged': event.flagged,
        'created_at': event.created_at.isoformat(),
        'interests_count': Interest.query.filter_by(event_id=event.id).count()
    } for event in events]
    
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_verified': user.is_verified
        },
        'events': events_list
    })

@admin_bp.route('/users/<int:user_id>/verify', methods=['PATCH'])
@jwt_required()
@admin_required
def verify_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user.is_verified = True
    db.session.commit()
    
    return jsonify({"message": "User verified as organizer successfully"})

@admin_bp.route('/users/<int:user_id>/unverify', methods=['PATCH'])
@jwt_required()
@admin_required
def unverify_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user.is_verified = False
    db.session.commit()
    
    return jsonify({"message": "User unverified successfully"})

@admin_bp.route('/users/<int:user_id>/ban', methods=['PATCH'])
@jwt_required()
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow banning other admins
    if user.is_admin:
        return jsonify({"message": "Cannot ban admin users"}), 400
    
    user.is_banned = True
    db.session.commit()
    
    return jsonify({"message": "User banned successfully"})

@admin_bp.route('/users/<int:user_id>/unban', methods=['PATCH'])
@jwt_required()
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user.is_banned = False
    db.session.commit()
    
    return jsonify({"message": "User unbanned successfully"})

@admin_bp.route('/analytics/events', methods=['GET'])
@jwt_required()
@admin_required
def get_events_analytics():
    # Total events count
    total_events = Event.query.count()
    pending_events = Event.query.filter_by(approved=False, flagged=False).count()
    approved_events = Event.query.filter_by(approved=True).count()
    flagged_events = Event.query.filter_by(flagged=True).count()
    
    # Events by category
    from sqlalchemy import func
    events_by_category = db.session.query(
        Event.category, 
        func.count(Event.id)
    ).group_by(Event.category).all()
    
    categories = {
        category: count for category, count in events_by_category
    }
    
    # Recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    recent = [{
        'id': event.id,
        'title': event.title,
        'category': event.category,
        'created_at': event.created_at.isoformat(),
        'approved': event.approved
    } for event in recent_events]
    
    return jsonify({
        'total_events': total_events,
        'pending_events': pending_events,
        'approved_events': approved_events,
        'flagged_events': flagged_events,
        'events_by_category': categories,
        'recent_events': recent
    })

@admin_bp.route('/analytics/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users_analytics():
    # Total users count
    total_users = User.query.count()
    verified_organizers = User.query.filter_by(is_verified=True).count()
    banned_users = User.query.filter_by(is_banned=True).count()
    
    # Top event creators
    from sqlalchemy import func
    top_creators = db.session.query(
        Event.created_by, 
        func.count(Event.id).label('event_count')
    ).group_by(Event.created_by).order_by(func.count(Event.id).desc()).limit(5).all()
    
    top_users = []
    for user_id, count in top_creators:
        user = User.query.get(user_id)
        if user:
            top_users.append({
                'id': user.id,
                'name': user.name,
                'event_count': count,
                'is_verified': user.is_verified
            })
    
    return jsonify({
        'total_users': total_users,
        'verified_organizers': verified_organizers,
        'banned_users': banned_users,
        'top_event_creators': top_users
    })