import os
from dotenv import load_dotenv

# Load environment variables (only in development)
try:
    load_dotenv()
except:
    pass  # In production (Vercel), we don't need dotenv

# Database configuration
DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'postgres.ypifadnzogapurytunmv'),
    'password': os.environ.get('DB_PASSWORD', 'ekanemiboro121'),
    'database': os.environ.get('DB_NAME', 'postgres'),
    'host': os.environ.get('DB_HOST', 'aws-0-eu-west-2.pooler.supabase.com'),
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