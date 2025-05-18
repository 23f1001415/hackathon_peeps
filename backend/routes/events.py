from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Event, User, Interest

events_bp = Blueprint('events', __name__)

@events_bp.route('', methods=['GET'])
def get_events():
    # Get query parameters for filtering
    category = request.args.get('category')
    location = request.args.get('location')
    
    # Start with all approved events
    query = Event.query.filter_by(approved=True)
    
    # Apply filters if provided
    if category:
        query = query.filter_by(category=category)
    if location:
        query = query.filter(Event.location.like(f'%{location}%'))
    
    # Order by date, most recent first
    events = query.order_by(Event.date).all()
    
    # Format events for response
    events_list = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'creator': User.query.get(event.created_by).name if User.query.get(event.created_by) else 'Unknown',
        'interests_count': Interest.query.filter_by(event_id=event.id).count()
    } for event in events]
    
    return jsonify(events_list)

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Don't show unapproved events unless to the creator
    if not event.approved:
        jwt_identity = get_jwt_identity() if request.headers.get('Authorization') else None
        if not jwt_identity or jwt_identity != event.created_by:
            return jsonify({"message": "Event not found or pending approval"}), 404
    
    # Get creator info
    creator = User.query.get(event.created_by)
    creator_name = creator.name if creator else 'Unknown'
    
    # Count interests
    interests_count = Interest.query.filter_by(event_id=event.id).count()
    
    return jsonify({
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'creator': creator_name,
        'is_verified_organizer': creator.is_verified if creator else False,
        'interests_count': interests_count,
        'created_at': event.created_at.isoformat(),
        'updated_at': event.updated_at.isoformat()
    })

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Validate required fields
    required_fields = ['title', 'description', 'category', 'location', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    # Validate category is one of the supported categories
    valid_categories = ['garage_sale', 'sports', 'community_class', 
                        'volunteer', 'exhibition', 'festival']
    if data['category'] not in valid_categories:
        return jsonify({"message": f"Invalid category. Must be one of: {', '.join(valid_categories)}"}), 400
    
    # Create new event
    try:
        event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    event = Event(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        location=data['location'],
        date=event_date,
        created_by=user_id,
        max_attendees=data.get('max_attendees'),
        approved=False  # Events need approval by default
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        "message": "Event created successfully and pending approval",
        "event_id": event.id
    }), 201

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    user_id = get_jwt_identity()
    
    # Only the creator can update the event
    if event.created_by != user_id:
        return jsonify({"message": "Unauthorized to update this event"}), 403
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        event.title = data['title']
    if 'description' in data:
        event.description = data['description']
    if 'category' in data:
        # Validate category is one of the supported categories
        valid_categories = ['garage_sale', 'sports', 'community_class', 
                           'volunteer', 'exhibition', 'festival']
        if data['category'] not in valid_categories:
            return jsonify({"message": f"Invalid category. Must be one of: {', '.join(valid_categories)}"}), 400
        event.category = data['category']
    if 'location' in data:
        event.location = data['location']
    if 'date' in data:
        try:
            event.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    if 'max_attendees' in data:
        event.max_attendees = data['max_attendees']
    
    # Set approved back to false if significant changes were made
    if 'title' in data or 'date' in data or 'location' in data:
        event.approved = False
    
    event.updated_at = datetime.utcnow()
    db.session.commit()
    
    # If event was modified significantly, notify users who showed interest
    # This would be implemented in notification service
    
    return jsonify({"message": "Event updated successfully"})

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    user_id = get_jwt_identity()
    
    # Only the creator or admin can delete the event
    user = User.query.get(user_id)
    if event.created_by != user_id and not user.is_admin:
        return jsonify({"message": "Unauthorized to delete this event"}), 403
    
    # Delete associated interests first
    Interest.query.filter_by(event_id=event_id).delete()
    
    # Delete the event
    db.session.delete(event)
    db.session.commit()
    
    # Would need to notify interested users about cancellation
    # This would be implemented in notification service
    
    return jsonify({"message": "Event deleted successfully"})

@events_bp.route('/my-events', methods=['GET'])
@jwt_required()
def get_my_events():
    user_id = get_jwt_identity()
    
    events = Event.query.filter_by(created_by=user_id).order_by(Event.date).all()
    
    events_list = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'category': event.category,
        'location': event.location,
        'date': event.date.isoformat(),
        'approved': event.approved,
        'flagged': event.flagged,
        'interests_count': Interest.query.filter_by(event_id=event.id).count()
    } for event in events]
    
    return jsonify(events_list)