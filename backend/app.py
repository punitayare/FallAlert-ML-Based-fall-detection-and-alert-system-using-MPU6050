from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import requests
from datetime import datetime, timedelta
from config import Config

# Import Firebase service
from services.firebase_service import (
    initialize_firebase,
    create_user, get_user, update_user,
    create_device, get_device, get_user_devices, update_device,
    verify_pairing_code, pair_device, update_device_heartbeat,
    save_sensor_data, get_sensor_data,
    create_fall_event, get_fall_event, update_fall_event,
    create_notification
)

# Import utilities
from utils.helpers import (
    generate_pairing_code, generate_device_id, generate_event_id,
    validate_pairing_code, format_timestamp
)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../web_dashboard/templates',
            static_folder='../web_dashboard/static')

app.config.from_object(Config)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SocketIO for real-time updates (using threading mode for Python 3.13 compatibility)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for tracking
connected_devices = {}
active_sessions = {}

# ============================================================================
# ROUTES - Basic Pages
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard alias"""
    return render_template('dashboard.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register():
    """Registration page"""
    return render_template('register.html')

@app.route('/devices')
def devices():
    """Device management page"""
    return render_template('devices.html')

@app.route('/monitoring')
def monitoring():
    """Real-time monitoring page"""
    return render_template('monitoring_new.html')

# ============================================================================
# API ROUTES - Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Fall Detection System',
        'version': '1.0.0'
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        'connected_devices': len(connected_devices),
        'active_sessions': len(active_sessions),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# ============================================================================
# API ROUTES - User Management
# ============================================================================

@app.route('/api/users/create', methods=['POST'])
def create_user_endpoint():
    """Create a new user in Firestore"""
    try:
        data = request.json or {}
        
        user_id = data.get('userId')
        email = data.get('email')
        name = data.get('name')
        
        # Validate inputs
        if not user_id or not email or not name:
            return jsonify({
                'success': False,
                'error': 'userId, email, and name are required'
            }), 400
        
        # Create user in Firebase
        result = create_user(user_id, email, name)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'userId': user_id,
                'email': email,
                'name': name
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    """Get user by ID"""
    try:
        user = get_user(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# API ROUTES - Device Management
# ============================================================================

@app.route('/api/devices/create', methods=['POST'])
def create_device_endpoint():
    """Create a new virtual device with 6-digit pairing code"""
    try:
        data = request.json or {}
        
        # Generate device ID and pairing code
        device_id = generate_device_id()
        pairing_code = generate_pairing_code()
        
        # Prepare device data
        device_data = {
            'deviceId': device_id,
            'deviceName': data.get('name', f'Device {pairing_code}'),
            'name': data.get('name', f'Device {pairing_code}'),  # Keep for backward compatibility
            'location': data.get('location', ''),
            'pairingCode': pairing_code,
            'batteryLevel': 100,
            'status': 'offline',
            'isPaired': False,
            'userId': data.get('userId')  # Store userId if provided
        }
        
        # Save to Firebase
        result = create_device(device_data)
        
        if 'error' in result:
            # Firebase not available - return mock data
            return jsonify({
                'success': True,
                'message': 'Device created (mock mode - no persistence)',
                'device': {
                    'deviceId': device_id,
                    'pairingCode': pairing_code,
                    'name': device_data['name'],
                    'location': device_data['location'],
                    'status': 'offline',
                    'isPaired': False,
                    'batteryLevel': 100,
                    'createdAt': datetime.utcnow().isoformat()
                }
            }), 200
        
        return jsonify({
            'success': True,
            'message': 'Device created successfully',
            'device': result
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices', methods=['GET'])
def list_devices_endpoint():
    """List user's devices"""
    try:
        # Get user_id from query params (in production, get from auth token)
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id required'
            }), 400
        
        # Get devices from Firebase
        devices = get_user_devices(user_id)
        
        # Return devices with all fields
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device_endpoint(device_id):
    """Delete a device"""
    try:
        from services.firebase_service import db as firestore_db
        
        # In production, verify user owns this device
        # For now, allow deletion
        
        if not firestore_db:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 500
        
        # Delete from Firestore
        firestore_db.collection('devices').document(device_id).delete()
        
        return jsonify({
            'success': True,
            'message': 'Device deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>/regenerate-code', methods=['POST'])
def regenerate_pairing_code_endpoint(device_id):
    """Regenerate pairing code for a device"""
    try:
        # Get device
        device = get_device(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Check if already paired
        if device.get('isPaired'):
            return jsonify({
                'success': False,
                'error': 'Cannot regenerate code for paired device'
            }), 400
        
        # Generate new code
        new_code = generate_pairing_code()
        
        # Calculate new expiry (15 minutes from now)
        expiry = datetime.utcnow() + timedelta(minutes=Config.PAIRING_CODE_EXPIRY_MINUTES)
        
        # Update device
        result = update_device(device_id, {
            'pairingCode': new_code,
            'pairingCodeExpiry': expiry.isoformat()
        })
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Pairing code regenerated successfully',
            'pairingCode': new_code,
            'expiresAt': expiry.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/heartbeat', methods=['POST'])
def device_heartbeat():
    """Update device status with heartbeat"""
    try:
        data = request.get_json()
        
        device_id = data.get('deviceId')
        battery_level = data.get('batteryLevel')
        status = data.get('status', 'online')
        
        if not device_id:
            return jsonify({
                'success': False,
                'error': 'Device ID is required'
            }), 400
        
        # Update device status
        update_data = {
            'status': status,
            'lastSeen': datetime.utcnow().isoformat()
        }
        
        if battery_level is not None:
            update_data['batteryLevel'] = battery_level
        
        result = update_device(device_id, update_data)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        # Broadcast device status update via WebSocket
        try:
            socketio.emit('device_status_update', {
                'deviceId': device_id,
                'status': status,
                'batteryLevel': battery_level,
                'lastSeen': update_data['lastSeen']
            }, namespace='/')
        except Exception as ws_error:
            print(f"Warning: WebSocket emit failed: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat received',
            'device': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/devices/pair', methods=['POST'])
def pair_device_endpoint():
    """Pair a device using pairing code"""
    try:
        data = request.get_json()
        
        device_id = data.get('deviceId')
        pairing_code = data.get('pairingCode')
        user_id = data.get('userId')
        
        if not all([device_id, pairing_code, user_id]):
            return jsonify({
                'success': False,
                'error': 'Device ID, pairing code, and user ID are required'
            }), 400
        
        # Get device
        device = get_device(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Verify pairing code
        if device.get('pairingCode') != pairing_code:
            return jsonify({
                'success': False,
                'error': 'Invalid pairing code'
            }), 400
        
        # Check if already paired - if so, just return success
        if device.get('isPaired'):
            return jsonify({
                'success': True,
                'message': 'Device already paired',
                'device': device
            }), 200
        
        # Update device as paired
        result = update_device(device_id, {
            'isPaired': True,
            'userId': user_id,
            'pairedAt': datetime.utcnow().isoformat(),
            'status': 'online'
        })
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Device paired successfully',
            'device': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# API ROUTES - Sensor Data
# ============================================================================





# ⏱️ Added: cooldown tracker to avoid multiple notifications
last_fall_time = {}
FALL_COOLDOWN_SECONDS = 30  # delay (in seconds) between two alerts for same device

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from devices and use ML API for fall detection"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        device_id = data.get('deviceId')
        
        if not device_id:
            return jsonify({'success': False, 'error': 'Device ID is required'}), 400
        
        # Get sensor data
        accel = data.get('accelerometer', {})
        gyro = data.get('gyroscope', {})
        
        # Store sensor data record
        sensor_record = {
            'deviceId': device_id,
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'accelerometer': accel,
            'gyroscope': gyro,
            'batteryLevel': data.get('batteryLevel'),
            'status': data.get('status', 'online')
        }
        
        # =====================================================================
        # ML API FALL DETECTION
        # =====================================================================
        
        fall_detected = False
        confidence = 0.0
        severity = 'none'
        detection_method = 'none'
        
        # Try ML API prediction
        if Config.ML_API_ENABLED:
            try:
                ml_response = requests.post(
                    f"{Config.ML_API_URL}/predict",
                    json={'accelerometer': accel, 'gyroscope': gyro},
                    timeout=Config.ML_API_TIMEOUT
                )
                
                if ml_response.status_code == 200:
                    ml_result = ml_response.json()
                    
                    if ml_result.get('success'):
                        fall_detected = ml_result.get('prediction', False)
                        confidence = ml_result.get('confidence', 0.0)
                        severity = ml_result.get('severity', 'none')
                        detection_method = 'ml_api'
                        print(f"✓ ML API prediction: fall={fall_detected}, confidence={confidence:.2%}")
                
            except requests.exceptions.Timeout:
                print(f"⚠️ ML API timeout - falling back to rule-based detection")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ ML API error: {e} - falling back to rule-based detection")
        
        # Fallback: Rule-based detection
        if detection_method == 'none':
            x, y, z = accel.get('x', 0), accel.get('y', 0), accel.get('z', 0)
            magnitude = (x**2 + y**2 + z**2) ** 0.5
            
            if magnitude > 20:
                fall_detected = True
                confidence = min(magnitude / 30.0, 1.0)
                severity = 'high' if magnitude > 25 else 'moderate'
                detection_method = 'rule_based'
                print(f"⚠️ Rule-based detection: magnitude={magnitude:.2f}")
        
        # =====================================================================
        # PROCESS FALL DETECTION
        # =====================================================================
        
        if fall_detected and confidence > 0.7:
            now = datetime.utcnow()
            last_time = last_fall_time.get(device_id)

            # ⏱️ Added: Skip notification if last one was too recent
            if last_time and (now - last_time).total_seconds() < FALL_COOLDOWN_SECONDS:
                print(f"⏸️ Skipping duplicate fall alert for {device_id} (cooldown active)")
                return jsonify({
                    'success': True,
                    'message': f"Duplicate fall ignored (cooldown {FALL_COOLDOWN_SECONDS}s)",
                    'fall_detection': {
                        'detected': True,
                        'confidence': confidence,
                        'severity': severity,
                        'method': detection_method
                    }
                }), 200

            last_fall_time[device_id] = now

            print(f"🚨 FALL DETECTED for device {device_id}!")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Severity: {severity}")
            print(f"   Method: {detection_method}")
            
            fall_event = {
                'deviceId': device_id,
                'timestamp': sensor_record['timestamp'],
                'accelerometer': accel,
                'gyroscope': gyro,
                'confidence': confidence,
                'severity': severity,
                'detection_method': detection_method,
                'status': 'detected',
                'notified': False
            }
            
            from services.firebase_service import db as firestore_db
            if firestore_db:
                try:
                    doc_ref = firestore_db.collection('fall_events').add(fall_event)
                    fall_event['id'] = doc_ref[1].id
                    print(f"✓ Fall event saved to Firebase: {fall_event['id']}")
                except Exception as e:
                    print(f"Error saving fall event: {e}")
            
            # Send FCM push notification
            try:
                from services.firebase_service import send_fcm_to_user, get_device
                device_doc = get_device(device_id)
                if device_doc and 'userId' in device_doc:
                    user_id = device_doc['userId']
                    device_name = device_doc.get('deviceName', 'Unknown Device')
                    
                    send_fcm_to_user(
                        user_id=user_id,
                        title=f"🚨 Fall Detected!",
                        body=f"{device_name} detected a fall ({confidence:.0%} confidence)",
                        data={
                            'type': 'fall_detected',
                            'deviceId': device_id,
                            'eventId': fall_event.get('id', ''),
                            'confidence': str(confidence),
                            'severity': severity
                        }
                    )
                else:
                    print(f"⚠️  Could not send FCM: device user_id not found")
            except Exception as fcm_error:
                print(f"Warning: FCM notification failed: {fcm_error}")
            
            if firestore_db:
                try:
                    sensor_record['fall_detection'] = {
                        'detected': True,
                        'confidence': confidence,
                        'severity': severity,
                        'method': detection_method
                    }
                    firestore_db.collection('sensor_data').add(sensor_record)
                    print(f"✓ Fall sensor data saved")
                except Exception as e:
                    print(f"Error saving sensor data: {e}")
        
        try:
            socketio.emit('sensor_data', sensor_record, to=device_id, namespace='/')
        except Exception as ws_error:
            print(f"Warning: WebSocket emit failed: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Sensor data received',
            'fall_detection': {
                'detected': fall_detected,
                'confidence': confidence,
                'severity': severity,
                'method': detection_method
            }
        }), 201
        
    except Exception as e:
        print(f"Error receiving sensor data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fall-events', methods=['GET'])
def get_fall_events():
    """Get fall events for a user or device"""
    try:
        user_id = request.args.get('userId')
        device_id = request.args.get('deviceId')
        limit = int(request.args.get('limit', 50))
        
        from services.firebase_service import db as firestore_db
        if not firestore_db:
            return jsonify({
                'success': True,
                'events': [],
                'count': 0
            }), 200
        
        # Query fall events
        query = firestore_db.collection('fall_events')
        
        if device_id:
            query = query.where('deviceId', '==', device_id)
        elif user_id:
            # Get user's devices first
            devices = get_user_devices(user_id)
            device_ids = [d['deviceId'] for d in devices]
            if not device_ids:
                return jsonify({
                    'success': True,
                    'events': [],
                    'count': 0
                }), 200
            query = query.where('deviceId', 'in', device_ids[:10])  # Firestore limit
        
        # Order by timestamp descending
        query = query.order_by('timestamp', direction='DESCENDING').limit(limit)
        
        events = []
        for doc in query.stream():
            event_data = doc.to_dict()
            event_data['id'] = doc.id
            events.append(event_data)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        }), 200
        
    except Exception as e:
        print(f"Error getting fall events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 
@app.route('/api/fall-alert', methods=['POST'])
def process_fall_alert():
    """Process fall detection alert (legacy endpoint)"""
    data = request.json
    device_id = data.get('device_id')
    
    print(f"🚨 Fall alert from device: {device_id}")
    
    return jsonify({
        'success': True,
        'message': 'Fall alert received - use /api/sensor-data endpoint instead',
        'alert_id': 'temp_alert_123'
    }), 200


@app.route('/api/notify', methods=['POST'])
def send_notification():
    """Send notification to mobile app"""
    # TODO: Implement Firebase Cloud Messaging
    return jsonify({
        'success': True,
        'message': 'Notification - FCM integration pending'
    }), 200

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"🔌 Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'message': 'Connected to Fall Detection System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"🔌 Client disconnected: {request.sid}")
    
    # Remove from any device rooms
    if request.sid in active_sessions:
        del active_sessions[request.sid]

@socketio.on('join_dashboard')
def handle_join_dashboard(data):
    """Join dashboard room for real-time updates"""
    user_id = data.get('userId')
    
    if user_id:
        join_room(f'user_{user_id}')
        active_sessions[request.sid] = {'userId': user_id, 'type': 'dashboard'}
        print(f"📊 Dashboard user joined: {user_id}")
        emit('joined_dashboard', {'userId': user_id, 'message': 'Subscribed to real-time updates'})

@socketio.on('join_device')
def handle_join_device(data):
    """Join device room for real-time updates"""
    device_id = data.get('device_id') or data.get('deviceId')
    
    if device_id:
        join_room(device_id)
        active_sessions[request.sid] = {'deviceId': device_id, 'type': 'device_monitor'}
        print(f"📱 Client joined device room: {device_id}")
        emit('joined_room', {'device_id': device_id, 'message': f'Monitoring device {device_id}'})

@socketio.on('leave_device')
def handle_leave_device(data):
    """Leave device room"""
    device_id = data.get('device_id') or data.get('deviceId')
    
    if device_id:
        leave_room(device_id)
        print(f"📱 Client left device room: {device_id}")
        emit('left_room', {'device_id': device_id})

@socketio.on('request_device_status')
def handle_request_device_status(data):
    """Request current status of all devices"""
    user_id = data.get('userId')
    
    if user_id:
        # Fetch devices for this user
        devices = get_user_devices(user_id)
        emit('device_status_batch', {'devices': devices, 'count': len(devices)})

@socketio.on('device_heartbeat')
def handle_device_heartbeat(data):
    """Handle device heartbeat"""
    device_id = data.get('device_id')
    battery = data.get('battery', 100)
    
    # Update in memory
    connected_devices[device_id] = {
        'last_heartbeat': datetime.utcnow().isoformat(),
        'battery': battery
    }
    
    # Update in Firebase
    update_device_heartbeat(device_id, battery)
    
    # Broadcast to monitoring dashboard
    emit('heartbeat_update', data, to=device_id)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Fall Detection System - Starting Server")
    print("=" * 60)
    print(f"Environment: {Config.FLASK_ENV}")
    print(f"Debug Mode: {Config.DEBUG}")
    print(f"Server: http://{Config.HOST}:{Config.PORT}")
    print("=" * 60)
    
    # Validate configuration
    Config.validate()
    
    # Initialize Firebase
    print("\n🔥 Initializing Firebase...")
    firebase_initialized = initialize_firebase()
    
    if firebase_initialized:
        print("✓ Firebase ready - using Firestore database")
    else:
        print("⚠️  Running without Firebase - using mock mode")
    
    print("=" * 60)
    print()
    
    # Run with SocketIO
    socketio.run(app, 
                 host=Config.HOST, 
                 port=Config.PORT, 
                 debug=Config.DEBUG,
                 use_reloader=Config.DEBUG)
