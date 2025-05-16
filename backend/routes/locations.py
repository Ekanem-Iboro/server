import re
from datetime import datetime
from ..database.models import Location, Device
from ..utils.auth import verify_token
from ..utils.http import success_response, error_response

def handle_location_routes(request):
    """
    Handle location routes.
    """
    path = request['path']
    method = request['method']
    
    # Authenticate user
    auth_header = request['auth_header']
    user_id = authenticate_request(auth_header)
    
    if not user_id:
        return error_response('Unauthorized', 401)
    
    # Update location
    if path == '/api/location/update' and method == 'POST':
        return handle_update_location(request, user_id)
    
    # Get current location
    elif re.match(r'^/api/location/current/\d+$', path) and method == 'GET':
        device_id = int(path.split('/')[-1])
        return handle_get_current_location(device_id, user_id)
    
    # Get location history
    elif re.match(r'^/api/location/history/\d+$', path) and method == 'GET':
        device_id = int(path.split('/')[-1])
        query_params = request['query_params']
        return handle_get_location_history(device_id, query_params, user_id)
    
    # Not found
    else:
        return error_response('Not found', 404)

def authenticate_request(auth_header):
    """
    Authenticate a request using the Authorization header.
    Returns the user ID if authenticated, None otherwise.
    """
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return verify_token(token)

def verify_device_ownership(device_id, user_id):
    """
    Verify that a device belongs to a user.
    """
    devices = Device.get_by_user_id(user_id)
    return any(device['id'] == device_id for device in devices)

def handle_update_location(request, user_id):
    """
    Handle POST /api/location/update
    """
    body = request['body']
    
    # Validate request body
    if not body:
        return error_response('Invalid request body')
    
    # Extract fields
    device_id = body.get('device_id')
    latitude = body.get('latitude')
    longitude = body.get('longitude')
    accuracy = body.get('accuracy')
    speed = body.get('speed')
    heading = body.get('heading')
    altitude = body.get('altitude')
    
    # Validate required fields
    if not device_id:
        return error_response('Device ID is required')
    
    if latitude is None:
        return error_response('Latitude is required')
    
    if longitude is None:
        return error_response('Longitude is required')
    
    # Verify device ownership
    if not verify_device_ownership(device_id, user_id):
        return error_response('Unauthorized', 401)
    
    try:
        # Create location
        location = Location.create(
            device_id,
            latitude,
            longitude,
            accuracy,
            speed,
            heading,
            altitude
        )
        
        return success_response({
            'location': location,
        }, 'Location updated successfully')
    
    except Exception as e:
        print(f"Error updating location: {e}")
        return error_response('Error updating location')

def handle_get_current_location(device_id, user_id):
    """
    Handle GET /api/location/current/{device_id}
    """
    # Verify device ownership
    if not verify_device_ownership(device_id, user_id):
        return error_response('Unauthorized', 401)
    
    try:
        # Get current location
        location = Location.get_current(device_id)
        
        if not location:
            return error_response('No location data found', 404)
        
        return success_response({'location': location})
    
    except Exception as e:
        print(f"Error getting current location: {e}")
        return error_response('Error getting current location')

def handle_get_location_history(device_id, query_params, user_id):
    """
    Handle GET /api/location/history/{device_id}
    """
    # Verify device ownership
    if not verify_device_ownership(device_id, user_id):
        return error_response('Unauthorized', 401)
    
    # Extract query parameters
    start = query_params.get('start', [None])[0]
    end = query_params.get('end', [None])[0]
    
    # Validate parameters
    if not start:
        return error_response('Start time is required')
    
    if not end:
        return error_response('End time is required')
    
    try:
        # Parse timestamps
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Get location history
        locations = Location.get_history(device_id, start_time, end_time)
        
        return success_response({'locations': locations})
    
    except ValueError:
        return error_response('Invalid timestamp format')
    
    except Exception as e:
        print(f"Error getting location history: {e}")
        return error_response('Error getting location history')
