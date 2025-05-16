import re
from ..database.models import Device
from ..utils.auth import verify_token
from ..utils.http import success_response, error_response

def handle_device_routes(request):
    """
    Handle device routes.
    """
    path = request['path']
    method = request['method']
    
    # Authenticate user
    auth_header = request['auth_header']
    user_id = authenticate_request(auth_header)
    
    if not user_id:
        return error_response('Unauthorized', 401)
    
    # Get all devices
    if path == '/api/devices' and method == 'GET':
        return handle_get_devices(user_id)
    
    # Create device
    elif path == '/api/devices' and method == 'POST':
        return handle_create_device(request, user_id)
    
    # Update device
    elif re.match(r'^/api/devices/\d+$', path) and method == 'PUT':
        device_id = int(path.split('/')[-1])
        return handle_update_device(request, device_id, user_id)
    
    # Delete device
    elif re.match(r'^/api/devices/\d+$', path) and method == 'DELETE':
        device_id = int(path.split('/')[-1])
        return handle_delete_device(device_id, user_id)
    
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

def handle_get_devices(user_id):
    """
    Handle GET /api/devices
    """
    try:
        devices = Device.get_by_user_id(user_id)
        return success_response({'devices': devices})
    
    except Exception as e:
        print(f"Error getting devices: {e}")
        return error_response('Error getting devices')

def handle_create_device(request, user_id):
    """
    Handle POST /api/devices
    """
    body = request['body']
    
    # Validate request body
    if not body:
        return error_response('Invalid request body')
    
    # Extract fields
    device_name = body.get('device_name')
    device_id = body.get('device_id')
    
    # Validate required fields
    if not device_name:
        return error_response('Device name is required')
    
    if not device_id:
        return error_response('Device ID is required')
    
    try:
        # Create device
        device = Device.create(user_id, device_name, device_id)
        
        return success_response({
            'device': device,
        }, 'Device created successfully')
    
    except Exception as e:
        print(f"Error creating device: {e}")
        return error_response('Error creating device')

def handle_update_device(request, device_id, user_id):
    """
    Handle PUT /api/devices/{id}
    """
    body = request['body']
    
    # Validate request body
    if not body:
        return error_response('Invalid request body')
    
    # Extract fields
    device_name = body.get('device_name')
    is_active = body.get('is_active')
    
    try:
        # Update device
        device = Device.update(device_id, device_name, is_active)
        
        if not device:
            return error_response('Device not found', 404)
        
        # Verify that the device belongs to the user
        if device['user_id'] != user_id:
            return error_response('Unauthorized', 401)
        
        return success_response({
            'device': device,
        }, 'Device updated successfully')
    
    except Exception as e:
        print(f"Error updating device: {e}")
        return error_response('Error updating device')

def handle_delete_device(device_id, user_id):
    """
    Handle DELETE /api/devices/{id}
    """
    try:
        # Get the device to verify ownership
        devices = Device.get_by_user_id(user_id)
        device_exists = any(device['id'] == device_id for device in devices)
        
        if not device_exists:
            return error_response('Device not found or unauthorized', 404)
        
        # Delete device
        success = Device.delete(device_id)
        
        if success:
            return success_response(message='Device deleted successfully')
        else:
            return error_response('Device not found', 404)
    
    except Exception as e:
        print(f"Error deleting device: {e}")
        return error_response('Error deleting device')
