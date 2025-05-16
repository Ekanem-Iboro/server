import json

def json_response(data, status_code=200):
    """
    Create a JSON HTTP response.
    """
    response = {
        'status': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': json.dumps(data),
    }
    
    return response

def success_response(data=None, message=None):
    """
    Create a success response.
    """
    response_data = {'success': True}
    
    if data is not None:
        response_data.update(data)
    
    if message is not None:
        response_data['message'] = message
    
    return json_response(response_data)

def error_response(message, status_code=400):
    """
    Create an error response.
    """
    return json_response({'success': False, 'message': message}, status_code)

def parse_json_body(body):
    """
    Parse a JSON request body.
    """
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None
