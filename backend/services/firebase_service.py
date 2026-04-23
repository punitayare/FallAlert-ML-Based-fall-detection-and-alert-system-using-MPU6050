"""
Firebase Service - Handles all Firebase operations
Includes Firestore database operations and initialization
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth, messaging
from datetime import datetime, timedelta
import os
from config import Config

# Global Firebase instances
db = None
firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global db, firebase_app
    
    try:
        # Check if already initialized
        if firebase_app is not None:
            print("✓ Firebase already initialized")
            return True
            
        # Get credentials path from config
        creds_path = Config.FIREBASE_CREDENTIALS_PATH
        
        if not creds_path or not os.path.exists(creds_path):
            print(f"⚠️  Firebase credentials not found at: {creds_path}")
            print("⚠️  Running in mock mode - no database persistence")
            return False
        
        # Initialize Firebase
        cred = credentials.Certificate(creds_path)
        firebase_app = firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        print("✓ Firebase initialized successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Firebase initialization failed: {str(e)}")
        print("⚠️  Running in mock mode - no database persistence")
        return False

def get_db():
    """Get Firestore database instance"""
    return db

# ============================================================================
# USER OPERATIONS
# ============================================================================

def create_user(user_id, email, name):
    """Create a new user in Firestore"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        user_data = {
            'userId': user_id,
            'email': email,
            'name': name,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        db.collection('users').document(user_id).set(user_data)
        return {'success': True, 'user': user_data}
        
    except Exception as e:
        return {'error': str(e)}

def get_user(user_id):
    """Get user by ID"""
    if db is None:
        return None
    
    try:
        doc = db.collection('users').document(user_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def update_user(user_id, data):
    """Update user data"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        data['updatedAt'] = datetime.utcnow()
        db.collection('users').document(user_id).update(data)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}

# ============================================================================
# DEVICE OPERATIONS
# ============================================================================

def create_device(device_data):
    """Create a new device"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        device_data['createdAt'] = datetime.utcnow()
        device_data['updatedAt'] = datetime.utcnow()
        device_data['status'] = 'offline'
        device_data['lastHeartbeat'] = None
        
        # Add pairing code expiry
        device_data['pairingCodeExpiry'] = datetime.utcnow() + timedelta(
            minutes=Config.PAIRING_CODE_EXPIRY_MINUTES
        )
        
        doc_ref = db.collection('devices').document(device_data['deviceId'])
        doc_ref.set(device_data)
        
        return {'success': True, 'device': device_data}
        
    except Exception as e:
        return {'error': str(e)}

def get_device(device_id):
    """Get device by ID"""
    if db is None:
        return None
    
    try:
        doc = db.collection('devices').document(device_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error getting device: {str(e)}")
        return None

def get_user_devices(user_id):
    """Get all devices for a user"""
    if db is None:
        return []
    
    try:
        devices = db.collection('devices').where('userId', '==', user_id).stream()
        device_list = []
        for doc in devices:
            device_data = doc.to_dict()
            # Ensure deviceName field exists (for backward compatibility)
            if 'deviceName' not in device_data and 'name' in device_data:
                device_data['deviceName'] = device_data['name']
            elif 'deviceName' not in device_data:
                device_data['deviceName'] = f"Device {device_data.get('pairingCode', 'Unknown')}"
            device_list.append(device_data)
        return device_list
    except Exception as e:
        print(f"Error getting user devices: {str(e)}")
        return []

def update_device(device_id, data):
    """Update device data"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        data['updatedAt'] = datetime.utcnow()
        db.collection('devices').document(device_id).update(data)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}

def verify_pairing_code(pairing_code):
    """Verify pairing code and return device if valid"""
    if db is None:
        return None
    
    try:
        # Query for device with this pairing code
        devices = db.collection('devices')\
            .where('pairingCode', '==', pairing_code)\
            .limit(1)\
            .stream()
        
        for doc in devices:
            device = doc.to_dict()
            
            # Check if code is expired
            if device.get('pairingCodeExpiry'):
                expiry = device['pairingCodeExpiry']
                if datetime.utcnow() > expiry:
                    return {'error': 'Pairing code expired'}
            
            # Check if already paired
            if device.get('userId'):
                return {'error': 'Device already paired'}
            
            return device
        
        return None
        
    except Exception as e:
        print(f"Error verifying pairing code: {str(e)}")
        return None

def pair_device(device_id, user_id):
    """Pair device with user"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        update_data = {
            'userId': user_id,
            'pairedAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'pairingCode': None,  # Clear pairing code after successful pairing
            'pairingCodeExpiry': None
        }
        
        db.collection('devices').document(device_id).update(update_data)
        return {'success': True}
        
    except Exception as e:
        return {'error': str(e)}

def update_device_heartbeat(device_id, battery_level=None):
    """Update device heartbeat timestamp"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        update_data = {
            'lastHeartbeat': datetime.utcnow(),
            'status': 'online',
            'updatedAt': datetime.utcnow()
        }
        
        if battery_level is not None:
            update_data['batteryLevel'] = battery_level
        
        db.collection('devices').document(device_id).update(update_data)
        return {'success': True}
        
    except Exception as e:
        return {'error': str(e)}

# ============================================================================
# SENSOR DATA OPERATIONS
# ============================================================================

def save_sensor_data(sensor_data):
    """Save sensor data to Firestore"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        sensor_data['timestamp'] = datetime.utcnow()
        
        # Add to sensor_data collection
        db.collection('sensor_data').add(sensor_data)
        
        return {'success': True}
        
    except Exception as e:
        return {'error': str(e)}

def get_sensor_data(device_id, limit=100):
    """Get recent sensor data for a device"""
    if db is None:
        return []
    
    try:
        data = db.collection('sensor_data')\
            .where('deviceId', '==', device_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()
        
        return [doc.to_dict() for doc in data]
        
    except Exception as e:
        print(f"Error getting sensor data: {str(e)}")
        return []

# ============================================================================
# FALL EVENT OPERATIONS
# ============================================================================

def create_fall_event(event_data):
    """Create a fall event"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        event_data['timestamp'] = datetime.utcnow()
        event_data['status'] = 'pending'  # pending, cancelled, escalated
        
        # Set cancellation deadline
        event_data['cancellationDeadline'] = datetime.utcnow() + timedelta(
            seconds=Config.FALL_CANCELLATION_WINDOW_SECONDS
        )
        
        # Set escalation deadline
        event_data['escalationDeadline'] = datetime.utcnow() + timedelta(
            minutes=Config.FALL_ESCALATION_WINDOW_MINUTES
        )
        
        doc_ref = db.collection('fall_events').add(event_data)
        event_data['eventId'] = doc_ref[1].id
        
        return {'success': True, 'event': event_data}
        
    except Exception as e:
        return {'error': str(e)}

def get_fall_event(event_id):
    """Get fall event by ID"""
    if db is None:
        return None
    
    try:
        doc = db.collection('fall_events').document(event_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error getting fall event: {str(e)}")
        return None

def update_fall_event(event_id, data):
    """Update fall event"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        data['updatedAt'] = datetime.utcnow()
        db.collection('fall_events').document(event_id).update(data)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}

def get_user_fall_events(user_id, limit=50):
    """Get fall events for a user"""
    if db is None:
        return []
    
    try:
        events = db.collection('fall_events')\
            .where('userId', '==', user_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()
        
        return [doc.to_dict() for doc in events]
        
    except Exception as e:
        print(f"Error getting fall events: {str(e)}")
        return []

# ============================================================================
# NOTIFICATION OPERATIONS
# ============================================================================

def create_notification(notification_data):
    """Create a notification"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        notification_data['timestamp'] = datetime.utcnow()
        notification_data['status'] = 'pending'  # pending, sent, failed
        
        doc_ref = db.collection('notifications').add(notification_data)
        notification_data['notificationId'] = doc_ref[1].id
        
        return {'success': True, 'notification': notification_data}
        
    except Exception as e:
        return {'error': str(e)}

def update_notification(notification_id, data):
    """Update notification status"""
    if db is None:
        return {"error": "Firebase not initialized"}
    
    try:
        data['updatedAt'] = datetime.utcnow()
        db.collection('notifications').document(notification_id).update(data)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}

def get_user_notifications(user_id, limit=50):
    """Get notifications for a user"""
    if db is None:
        return []
    
    try:
        notifications = db.collection('notifications')\
            .where('userId', '==', user_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()
        
        return [doc.to_dict() for doc in notifications]
        
    except Exception as e:
        print(f"Error getting notifications: {str(e)}")
        return []

def send_fcm_notification(token, title, body, data=None):
    """Send FCM push notification to a device"""
    try:
        if not token:
            print("⚠️  No FCM token provided")
            return False
            
        # Create notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        
        # Send message
        response = messaging.send(message)
        print(f"✓ FCM notification sent successfully: {response} to token: {token}")
        return True
        
    except Exception as e:
        print(f"✗ Error sending FCM notification: {str(e)}")
        return False

def send_fcm_to_user(user_id, title, body, data=None):
    """Send FCM notification to all devices of a user"""
    try:
        # Get user's FCM tokens from Firestore
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            print(f"⚠️  User not found: {user_id}")
            return False
            
        user_data = user_doc.to_dict()
        fcm_tokens = user_data.get('fcmTokens', [])
        
        if not fcm_tokens:
            print(f"⚠️  No FCM tokens found for user: {user_id}")
            return False
        
        # Send to all tokens
        success_count = 0
        for token in fcm_tokens:
            if send_fcm_notification(token, title, body, data):
                success_count += 1
        
        print(f"✓ Sent FCM to {success_count}/{len(fcm_tokens)} devices")
        return success_count > 0
        
    except Exception as e:
        print(f"✗ Error sending FCM to user: {str(e)}")
        return False
