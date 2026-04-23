"""
Utility functions for the Fall Detection System
"""

import random
import string
from datetime import datetime
import uuid

def generate_pairing_code(length=6):
    """
    Generate a random 6-digit pairing code
    Returns a string of digits
    """
    return ''.join(random.choices(string.digits, k=length))

def generate_device_id():
    """
    Generate a unique device ID
    Format: device_xxxxxxxx
    """
    unique_id = str(uuid.uuid4())[:8]
    return f"device_{unique_id}"

def generate_event_id():
    """
    Generate a unique event ID
    Format: event_xxxxxxxx
    """
    unique_id = str(uuid.uuid4())[:8]
    return f"event_{unique_id}"

def is_code_expired(expiry_time):
    """
    Check if a timestamp has expired
    """
    if expiry_time is None:
        return True
    return datetime.utcnow() > expiry_time

def format_timestamp(dt):
    """
    Format datetime for API responses
    """
    if dt is None:
        return None
    return dt.isoformat()

def validate_email(email):
    """
    Basic email validation
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_pairing_code(code):
    """
    Validate pairing code format
    Should be 6 digits
    """
    return code.isdigit() and len(code) == 6
