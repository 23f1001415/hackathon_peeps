from flask_mail import Mail, Message
from flask import current_app
import requests
import json
from datetime import datetime, timedelta
from models import Event, Interest, User
import threading

mail = Mail()

def init_notification_service(app):
    """Initialize the notification service with the Flask app"""
    mail.init_app(app)

def send_email(subject, recipients, body, html=None):
    """Send an email using Flask-Mail"""
    try:
        msg = Message(subject, recipients=recipients)
        msg.body = body
        if html:
            msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_sms(to, body):
    """Send SMS using a third-party service (e.g., Twilio)"""
    try:
        # This is a placeholder for SMS integration
        # Replace with actual Twilio or similar service integration
        # Example Twilio implementation:
        
        # from twilio.rest import Client
        # account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        # auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=body,
        #     from_=current_app.config.get('TWILIO_PHONE_NUMBER'),
        #     to=to
        # )
        # return message.sid
        
        # For now, just log the message
        current_app.logger.info(f"SMS would be sent to {to}: {body}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False

def send_whatsapp(to, body):
    """Send WhatsApp message using a third-party service"""
    try:
        # This is a placeholder for WhatsApp integration
        # Replace with actual WhatsApp Business API integration
        
        # Example implementation using WhatsApp Business API:
        # url = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
        # headers = {
        #     "Authorization": f"Bearer {current_app.config.get('WHATSAPP_API_TOKEN')}",
        #     "Content-Type": "application/json"
        # }
        # data = {
        #     "messaging_product": "whatsapp",
        #     "to": to,
        #     "type": "text",
        #     "text": {"body": body}
        # }
        # response = requests.post(url, headers=headers, data=json.dumps(data))
        # return response.status_code == 200
        
        # For now, just log the message
        current_app.logger.info(f"WhatsApp would be sent to {to}: {body}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return False

def notify_event_interest(event_id, interest_id):
    """Notify event creator about a new interest"""
    from ..models import db
    
    event = Event.query.get(event_id)
    interest = Interest.query.get(interest_id)
    
    if not event or not interest:
        return False
    
    creator = User.query.get(event.created_by)
    
    if not creator:
        return False
    
    subject = f"New interest in your event: {event.title}"
    body = f"""
    Hello {creator.name},
    
    Someone has shown interest in attending your event "{event.title}".
    
    Attendee details:
    - Name: {interest.user_name}
    - Email: {interest.email}
    - Phone: {interest.phone}
    - Number of attendees: {interest.attendees}
    
    You can view all interests for this event in your dashboard.
    
    Community Pulse Team
    """
    
    return send_email(subject, [creator.email], body)

def notify_event_approval(event_id, approved=True):
    """Notify event creator about approval/rejection"""
    event = Event.query.get(event_id)
    
    if not event:
        return False
    
    creator = User.query.get(event.created_by)
    
    if not creator:
        return False
    
    status = "approved" if approved else "rejected"
    subject = f"Your event has been {status}: {event.title}"
    body = f"""
    Hello {creator.name},
    
    Your event "{event.title}" has been {status} by our administrators.
    
    {
        "It is now visible to all users and people can register their interest." 
        if approved else 
        "Please review our community guidelines and consider making changes to resubmit the event."
    }
    
    Event Details:
    - Title: {event.title}
    - Date: {event.date.strftime('%A, %B %d, %Y at %I:%M %p')}
    - Location: {event.location}
    
    Community Pulse Team
    """
    
    return send_email(subject, [creator.email], body)

def notify_event_update(event_id, changes=None):
    """Notify all interested users about event updates"""
    event = Event.query.get(event_id)
    
    if not event:
        return False
    
    interests = Interest.query.filter_by(event_id=event_id).all()
    
    if not interests:
        return True  # No one to notify
    
    subject = f"Event Update: {event.title}"
    body = f"""
    Hello {{name}},
    
    The event "{event.title}" that you're interested in has been updated.
    
    {
        '\n'.join([f"- {change}" for change in changes]) 
        if changes 
        else "Please check the event page for the latest details."
    }
    
    Updated Event Details:
    - Title: {event.title}
    - Date: {event.date.strftime('%A, %B %d, %Y at %I:%M %p')}
    - Location: {event.location}
    
    You can view the complete details on the Community Pulse platform.
    
    Community Pulse Team
    """
    
    success_count = 0
    
    for interest in interests:
        # Personalize the email for each recipient
        personalized_body = body.replace("{name}", interest.user_name)
        success = send_email(subject, [interest.email], personalized_body)
        
        if success:
            success_count += 1
            
        # Send SMS if phone is available
        if interest.phone:
            sms_body = f"Event Update: {event.title} has been updated. Please check your email for details."
            send_sms(interest.phone, sms_body)
    
    return success_count == len(interests)

def schedule_event_reminders():
    """
    Schedule reminders for events happening tomorrow
    This should be called by a scheduler (e.g., Celery beat or APScheduler)
    """
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    next_day = tomorrow + timedelta(days=1)
    
    # Get all approved events happening tomorrow
    events = Event.query.filter(
        Event.approved == True,
        Event.date >= tomorrow,
        Event.date < next_day
    ).all()
    
    for event in events:
        # Get all interests for this event
        interests = Interest.query.filter_by(event_id=event.id).all()
        
        if not interests:
            continue
        
        subject = f"Reminder: {event.title} is happening tomorrow"
        body = f"""
        Hello {{name}},
        
        This is a reminder that the event "{event.title}" is happening tomorrow.
        
        Event Details:
        - Date: {event.date.strftime('%A, %B %d, %Y at %I:%M %p')}
        - Location: {event.location}
        
        We're looking forward to seeing you there!
        
        Community Pulse Team
        """
        
        for interest in interests:
            # Personalize the email for each recipient
            personalized_body = body.replace("{name}", interest.user_name)
            send_email(subject, [interest.email], personalized_body)
            
            # Send SMS if phone is available
            if interest.phone:
                sms_body = f"Reminder: {event.title} is happening tomorrow at {event.date.strftime('%I:%M %p')}. Location: {event.location}"
                send_sms(interest.phone, sms_body)

def notify_event_cancellation(event_id):
    """Notify all interested users about event cancellation"""
    event = Event.query.get(event_id)
    
    if not event:
        return False
    
    interests = Interest.query.filter_by(event_id=event_id).all()
    
    if not interests:
        return True  # No one to notify
    
    subject = f"Event Cancelled: {event.title}"
    body = f"""
    Hello {{name}},
    
    We regret to inform you that the event "{event.title}" has been cancelled.
    
    Event Details:
    - Title: {event.title}
    - Date: {event.date.strftime('%A, %B %d, %Y at %I:%M %p')}
    - Location: {event.location}
    
    We apologize for any inconvenience this may cause.
    
    Community Pulse Team
    """
    
    success_count = 0
    
    for interest in interests:
        # Personalize the email for each recipient
        personalized_body = body.replace("{name}", interest.user_name)
        success = send_email(subject, [interest.email], personalized_body)
        
        if success:
            success_count += 1
            
        # Send SMS if phone is available
        if interest.phone:
            sms_body = f"Event Cancelled: {event.title} has been cancelled. Please check your email for details."
            send_sms(interest.phone, sms_body)
    
    return success_count == len(interests)

# Background task helper function
def run_async(func, *args, **kwargs):
    """Run a function asynchronously"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread