import jwt
import time
import hashlib
from ..config import JWT_CONFIG

def generate_token(user_id):
    """
    Generate a JWT token for a user.
    """
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + (JWT_CONFIG['token_expiry_minutes'] * 60),
        'iat': int(time.time()),
    }
    
    token = jwt.encode(
        payload,
        JWT_CONFIG['secret_key'],
        algorithm=JWT_CONFIG['algorithm']
    )
    
    return token

def verify_token(token):
    """
    Verify a JWT token and return the user ID if valid.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_CONFIG['secret_key'],
            algorithms=[JWT_CONFIG['algorithm']]
        )
        
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None

def hash_password(password):
    """
    Hash a password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """
    Verify a password against a hash.
    """
    return hash_password(password) == password_hash
