from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import warnings

app = Flask(__name__)
CORS(app)

# Load the trained model
MODEL_PATH = 'fall_model.pkl'
model = None

def generate_model_if_needed():
    """Generate a simple model if loading fails"""
    from sklearn.ensemble import RandomForestClassifier
    
    print("Generating fallback model...")
    # Simple training data
    np.random.seed(42)
    X_normal = np.random.normal([0, 0, 9.8, 0, 0, 0], [2, 2, 1, 0.5, 0.5, 0.5], (500, 6))
    X_fall = np.random.normal([15, 15, 25, 3, 3, 3], [8, 8, 10, 2, 2, 2], (500, 6))
    X = np.vstack([X_normal, X_fall])
    y = np.hstack([np.zeros(500), np.ones(500)])
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)
    
    # Save it
    joblib.dump(model, MODEL_PATH)
    print(f"✓ Generated and saved new model to {MODEL_PATH}")
    return model

def load_model():
    """Load the fall detection model"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            # Suppress version warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                model = joblib.load(MODEL_PATH)
            print(f"✓ Model loaded successfully from {MODEL_PATH}")
            return True
        else:
            print(f"✗ Model file not found: {MODEL_PATH}")
            print("Generating new model...")
            model = generate_model_if_needed()
            return model is not None
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("Attempting to generate new model...")
        try:
            model = generate_model_if_needed()
            return model is not None
        except Exception as gen_error:
            print(f"✗ Failed to generate model: {gen_error}")
            return False

# Load model on startup
load_model()

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API information"""
    return jsonify({
        'service': 'Fall Detection ML API',
        'version': '1.0.0',
        'status': 'running',
        'model_loaded': model is not None,
        'endpoints': {
            'health': '/health',
            'predict': '/predict (POST)',
            'batch_predict': '/batch-predict (POST)'
        },
        'documentation': 'https://github.com/devendra011396/fall-simulated'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'service': 'Fall Detection ML API',
        'version': '1.0.0'
    }), 200

@app.route('/predict', methods=['POST'])
def predict_fall():
    """
    Predict if sensor data indicates a fall
    
    Expected JSON format:
    {
        "accelerometer": {"x": 0.5, "y": 0.3, "z": 9.8},
        "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.3}
    }
    """
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract sensor data
        accel = data.get('accelerometer', {})
        gyro = data.get('gyroscope', {})
        
        # Create feature vector [accelX, accelY, accelZ, gyroX, gyroY, gyroZ]
        features = np.array([[
            accel.get('x', 0),
            accel.get('y', 0),
            accel.get('z', 9.8),
            gyro.get('x', 0),
            gyro.get('y', 0),
            gyro.get('z', 0)
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        is_fall = bool(prediction == 1)
        confidence = float(probabilities[1])  # Probability of fall class
        
        # Calculate severity based on confidence
        if confidence > 0.9:
            severity = 'critical'
        elif confidence > 0.7:
            severity = 'high'
        elif confidence > 0.5:
            severity = 'moderate'
        else:
            severity = 'low'
        
        return jsonify({
            'success': True,
            'prediction': is_fall,
            'confidence': confidence,
            'severity': severity,
            'probabilities': {
                'normal': float(probabilities[0]),
                'fall': float(probabilities[1])
            },
            'method': 'random_forest'
        }), 200
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Predict multiple sensor data points
    
    Expected JSON format:
    {
        "data": [
            {"accelerometer": {...}, "gyroscope": {...}},
            {"accelerometer": {...}, "gyroscope": {...}}
        ]
    }
    """
    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        data = request.get_json()
        sensor_data_list = data.get('data', [])
        
        if not sensor_data_list:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        results = []
        
        for sensor_data in sensor_data_list:
            accel = sensor_data.get('accelerometer', {})
            gyro = sensor_data.get('gyroscope', {})
            
            features = np.array([[
                accel.get('x', 0),
                accel.get('y', 0),
                accel.get('z', 9.8),
                gyro.get('x', 0),
                gyro.get('y', 0),
                gyro.get('z', 0)
            ]])
            
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            results.append({
                'is_fall': bool(prediction == 1),
                'confidence': float(probabilities[1])
            })
        
        return jsonify({
            'success': True,
            'predictions': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
