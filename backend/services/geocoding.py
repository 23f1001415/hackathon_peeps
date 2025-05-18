import requests
from flask import current_app
import json
from functools import lru_cache

class GeocodingService:
    """
    Service to handle geocoding operations
    - Convert addresses to coordinates (geocoding)
    - Get address from coordinates (reverse geocoding)
    - Calculate distance between locations
    - Search for nearby events
    """
    
    def __init__(self, app=None):
        self.api_key = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app configuration"""
        self.api_key = app.config.get('GEOCODING_API_KEY')
    
    @lru_cache(maxsize=128)
    def geocode(self, address):
        """Convert address to coordinates (latitude, longitude)"""
        if not self.api_key:
            current_app.logger.warning("Geocoding API key not set")
            return None
        
        try:
            # Using OpenStreetMap Nominatim API as an example
            # In production, consider using Google Maps, Mapbox, or other commercial APIs
            
            # Nominatim doesn't require API key but has usage limits
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            
            # If using Google Maps API:
            # url = f"https://maps.googleapis.com/maps/api/geocode/json"
            # params = {
            #     'address': address,
            #     'key': self.api_key
            # }
            
            headers = {
                'User-Agent': 'CommunityPulseApp/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    location = data[0]
                    return {
                        'latitude': float(location['lat']),
                        'longitude': float(location['lon']),
                        'display_name': location['display_name']
                    }
            
            return None
        
        except Exception as e:
            current_app.logger.error(f"Geocoding error: {str(e)}")
            return None
    
    @lru_cache(maxsize=128)
    def reverse_geocode(self, latitude, longitude):
        """Convert coordinates to address"""
        if not self.api_key:
            current_app.logger.warning("Geocoding API key not set")
            return None
        
        try:
            # Using OpenStreetMap Nominatim API as an example
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json'
            }
            
            # If using Google Maps API:
            # url = f"https://maps.googleapis.com/maps/api/geocode/json"
            # params = {
            #     'latlng': f"{latitude},{longitude}",
            #     'key': self.api_key
            # }
            
            headers = {
                'User-Agent': 'CommunityPulseApp/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    return {
                        'address': data.get('display_name', ''),
                        'city': data.get('address', {}).get('city', ''),
                        'state': data.get('address', {}).get('state', ''),
                        'country': data.get('address', {}).get('country', '')
                    }
            
            return None
        
        except Exception as e:
            current_app.logger.error(f"Reverse geocoding error: {str(e)}")
            return None
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the distance between two points on Earth
        using the Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Differences
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def find_nearby_events(self, db, latitude, longitude, radius=10.0):
        """
        Find events within a certain radius of the given coordinates
        
        Args:
            db: SQLAlchemy database instance
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in kilometers (default: 10km)
        
        Returns:
            List of events within the specified radius
        """
        from ..models import Event
        from sqlalchemy import or_
        
        # This is a simple approach that requires geocoding all event locations
        # In a production environment, consider using PostGIS or specialized geo databases
        
        all_events = Event.query.filter(Event.approved == True).all()
        nearby_events = []
        
        for event in all_events:
            # Get coordinates for event location
            event_coords = self.geocode(event.location)
            
            if event_coords:
                # Calculate distance
                distance = self.calculate_distance(
                    latitude, longitude,
                    event_coords['latitude'], event_coords['longitude']
                )
                
                # If within radius, add to results
                if distance <= radius:
                    event_dict = {
                        'id': event.id,
                        'title': event.title,
                        'description': event.description,
                        'category': event.category,
                        'location': event.location,
                        'date': event.date.isoformat(),
                        'distance': round(distance, 2)  # Distance in km
                    }
                    nearby_events.append(event_dict)
        
        # Sort by distance
        nearby_events.sort(key=lambda x: x['distance'])
        
        return nearby_events
    
    def search_by_region(self, db, region):
        """
        Search for events in a particular region (city, state, country)
        
        Args:
            db: SQLAlchemy database instance
            region: Name of the region to search in
        
        Returns:
            List of events in the specified region
        """
        from ..models import Event
        from sqlalchemy import or_
        
        # This is a simple implementation
        # In a production environment, consider using geographic databases
        
        # Search for events with location containing the region name
        events = Event.query.filter(
            Event.approved == True,
            or_(
                Event.location.ilike(f'%{region}%')
            )
        ).all()
        
        result = []
        for event in events:
            result.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'location': event.location,
                'date': event.date.isoformat()
            })
        
        return result

# Create service instance
geocoding_service = GeocodingService()