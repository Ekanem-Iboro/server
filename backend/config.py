# # Database configuration
# DB_CONFIG = {
#     'user': 'postgres',
#     'password': 'ekanemiboro121',
#     'database': 'phone_tracker',
#     'host': 'localhost',
#     'port': '5432',
# }

# # Server configuration
# SERVER_CONFIG = {
#     'host': '0.0.0.0',  # Listen on all network interfaces
#     'port': 8000,       # Default port
#     'timeout': 30       # Socket timeout in seconds
# }

# # JWT configuration
# JWT_CONFIG = {
#     'secret_key': 'Ej8p$2xK!7mLqZ@5vNfR*tYbAc3DgW6H9sTuV4X',  # Secure random key for production
#     'algorithm': 'HS256',
#     'token_expiry_minutes': 60 * 24,  # 24 hours
# }

# # Rate limiting configuration
# RATE_LIMIT_CONFIG = {
#     'requests_per_minute': 60,
# }

import os

# Database configuration
DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'ekanemiboro121'),
    'database': os.environ.get('DB_NAME', 'phone_tracker'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
}

# Server configuration
SERVER_CONFIG = {
    'host': os.environ.get('SERVER_HOST', '0.0.0.0'),
    'port': int(os.environ.get('PORT', 8000)),
    'timeout': int(os.environ.get('SERVER_TIMEOUT', 30))
}

# JWT configuration
JWT_CONFIG = {
    'secret_key': os.environ.get('JWT_SECRET', 'Ej8p$2xK!7mLqZ@5vNfR*tYbAc3DgW6H9sTuV4X'),
    'algorithm': 'HS256',
    'token_expiry_minutes': int(os.environ.get('JWT_EXPIRY', 60 * 24)),
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    'requests_per_minute': int(os.environ.get('RATE_LIMIT', 60)),
}