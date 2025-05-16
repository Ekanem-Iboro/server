import time
from collections import defaultdict
from ..config import RATE_LIMIT_CONFIG

# Store request counts per IP address
request_counts = defaultdict(list)

def is_rate_limited(ip_address):
    """
    Check if an IP address is rate limited.
    Returns True if rate limited, False otherwise.
    """
    current_time = time.time()
    
    # Remove requests older than 1 minute
    request_counts[ip_address] = [
        timestamp for timestamp in request_counts[ip_address]
        if current_time - timestamp < 60
    ]
    
    # Check if the number of requests in the last minute exceeds the limit
    if len(request_counts[ip_address]) >= RATE_LIMIT_CONFIG['requests_per_minute']:
        return True
    
    # Add the current request
    request_counts[ip_address].append(current_time)
    
    return False
