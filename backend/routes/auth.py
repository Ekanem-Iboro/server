from ..database.models import User
from ..utils.auth import generate_token, verify_token
from ..utils.http import success_response, error_response

def handle_auth_routes(request):
    """
    Handle authentication routes.
    """
    path = request['path']
    method = request['method']

    # Register route
    if path == '/api/auth/register':
        if method == 'POST':
            return handle_register(request)
        elif method == 'GET':
            return handle_register_info()

    # Login route
    elif path == '/api/auth/login':
        if method == 'POST':
            return handle_login(request)
        elif method == 'GET':
            return handle_login_info()

    # Logout route
    elif path == '/api/auth/logout':
        if method == 'POST':
            return handle_logout(request)
        elif method == 'GET':
            return handle_logout_info()

    # Not found
    else:
        return error_response('Not found', 404)

def handle_register_info():
    """
    Provide information about the register endpoint.
    """
    info = {
        "endpoint": "/api/auth/register",
        "method": "POST",
        "description": "Register a new user",
        "required_fields": {
            "phone_number": "User's phone number (string)",
            "name": "User's full name (string)",
            "email": "User's email address (string)",
            "password": "User's password (string, min 8 characters)"
        },
        "example_request": {
            "phone_number": "+1234567890",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword"
        }
    }
    return success_response(info, "Register endpoint information")

def handle_login_info():
    """
    Provide information about the login endpoint.
    """
    info = {
        "endpoint": "/api/auth/login",
        "method": "POST",
        "description": "Login a user",
        "required_fields": {
            "phone_number": "User's phone number (string)",
            "password": "User's password (string)"
        },
        "example_request": {
            "phone_number": "+1234567890",
            "password": "securepassword"
        }
    }
    return success_response(info, "Login endpoint information")

def handle_logout_info():
    """
    Provide information about the logout endpoint.
    """
    info = {
        "endpoint": "/api/auth/logout",
        "method": "POST",
        "description": "Logout a user",
        "required_headers": {
            "Authorization": "Bearer <token>"
        }
    }
    return success_response(info, "Logout endpoint information")

def handle_register(request):
    """
    Handle user registration.
    """
    body = request['body']

    # Validate request body
    if not body:
        return error_response('Invalid request body')

    # Extract fields
    phone_number = body.get('phone_number')
    name = body.get('name')
    email = body.get('email')
    password = body.get('password')

    # Validate required fields
    if not phone_number:
        return error_response('Phone number is required')

    if not name:
        return error_response('Name is required')

    if not email:
        return error_response('Email is required')

    if not password:
        return error_response('Password is required')

    # Validate password length
    if len(password) < 8:
        return error_response('Password must be at least 8 characters')

    try:
        # Create user
        user = User.create(phone_number, name, email, password)

        # Generate token
        token = generate_token(user['id'])

        return success_response({
            'user': user,
            'token': token,
        }, 'User registered successfully')

    except Exception as e:
        # Handle duplicate key errors
        if 'duplicate key' in str(e).lower():
            if 'phone_number' in str(e).lower():
                return error_response('Phone number already registered')
            elif 'email' in str(e).lower():
                return error_response('Email already registered')

        # Handle other errors
        print(f"Error registering user: {e}")
        return error_response('Error registering user')

def handle_login(request):
    """
    Handle user login.
    """
    body = request['body']

    # Validate request body
    if not body:
        return error_response('Invalid request body')

    # Extract fields
    phone_number = body.get('phone_number')
    password = body.get('password')

    # Validate required fields
    if not phone_number:
        return error_response('Phone number is required')

    if not password:
        return error_response('Password is required')

    try:
        # Authenticate user
        user = User.authenticate(phone_number, password)

        if not user:
            return error_response('Invalid phone number or password', 401)

        # Generate token
        token = generate_token(user['id'])

        return success_response({
            'user': user,
            'token': token,
        }, 'Login successful')

    except Exception as e:
        print(f"Error logging in: {e}")
        return error_response('Error logging in')

def handle_logout(request):
    """
    Handle user logout.
    """
    # No server-side action needed for logout
    # The client should discard the token
    return success_response(message='Logout successful')
