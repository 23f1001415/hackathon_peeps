from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import db, Interest, Event, User
from functools import wraps

interests_bp = Blueprint('interests', __name__)

@interests_bp.route('/<int:event_id>', methods=['POST'])
def register_interest(event_id):
    # Get event
    event = Event.query.get_or_404(event_id)
    
    # Check if event is approved
    if not event.approved:
        return jsonify({"message": "Cannot register interest for unapproved events"}), 400
    
    # Check if event has already happened
    from datetime import datetime
    if event.date < datetime.utcnow():
        return jsonify({"message": "Cannot register interest for past events"}), 400
    
    # Check if event has max_attendees and if it's already reached
    if event.max_attendees is not None:
        current_attendees = Interest.query.filter_by(event_id=event_id).count()
        if current_attendees >= event.max_attendees:
            return jsonify({"message": "Event has reached maximum capacity"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_name', 'email', 'phone', 'attendees']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    # Check if user is authenticated
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        pass
    
    # Check if email already registered interest for this event
    existing_interest = Interest.query.filter_by(
        email=data['email'], 
        event_id=event_id
    ).first()
    
    if existing_interest:
        return jsonify({"message": "You have already registered interest for this event"}), 409
    
    # Create new interest
    interest = Interest(
        user_name=data['user_name'],
        email=data['email'],
        phone=data['phone'],
        attendees=data['attendees'],
        event_id=event_id,
        user_id=user_id
    )
    
    db.session.add(interest)
    db.session.commit()
    
    # Here you would trigger a notification for the event organizer
    # And add the person to the list for event notifications
    
    return jsonify({
        "message": "Interest registered successfully",
        "interest_id": interest.id
    }), 201

@interests_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_interests(event_id):
    user_id = get_jwt_identity()
    
    # Check if the user is the creator or an admin
    event = Event.query.get_or_404(event_id)
    user = User.query.get(user_id)
    
    if event.created_by != user_id and not user.is_admin:
        return jsonify({"message": "Unauthorized to view interests for this event"}), 403
    
    interests = Interest.query.filter_by(event_id=event_id).all()
    
    interests_list = [{
        'id': interest.id,
        'user_name': interest.user_name,
        'email': interest.email,
        'phone': interest.phone,
        'attendees': interest.attendees,
        'created_at': interest.created_at.isoformat(),
        'user_id': interest.user_id
    } for interest in interests]
    
    total_attendees = sum(interest.attendees for interest in interests)
    
    return jsonify({
        'interests': interests_list,
        'total_count': len(interests_list),
        'total_attendees': total_attendees
    })

@interests_bp.route('/my-interests', methods=['GET'])
@jwt_required()
def get_my_interests():
    user_id = get_jwt_identity()
    
    # Get all interests for this user
    interests = Interest.query.filter_by(user_id=user_id).all()
    
    result = []
    for interest in interests:
        event = Event.query.get(interest.event_id)
        if event:
            result.append({
                'interest_id': interest.id,
                'event_id': event.id,
                'event_title': event.title,
                'event_category': event.category,
                'event_location': event.location,
                'event_date': event.date.isoformat(),
                'attendees': interest.attendees,
                'registered_at': interest.created_at.isoformat()
            })
    
    return jsonify(result)

@interests_bp.route('/<int:interest_id>', methods=['DELETE'])
@jwt_required()
def cancel_interest(interest_id):
    user_id = get_jwt_identity()
    
    interest = Interest.query.get_or_404(interest_id)
    
    # Check if the user is the one who registered or an admin
    user = User.query.get(user_id)
    if interest.user_id != user_id and not user.is_admin:
        return jsonify({"message": "Unauthorized to cancel this interest"}), 403
    
    db.session.delete(interest)
    db.session.commit()
    
    return jsonify({"message": "Interest cancelled successfully"})