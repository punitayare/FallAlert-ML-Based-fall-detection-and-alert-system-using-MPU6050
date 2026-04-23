import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # ML API
    ML_API_URL = os.getenv('ML_API_URL', 'http://localhost:5001')
    ML_API_TIMEOUT = int(os.getenv('ML_API_TIMEOUT', '5'))
    ML_API_ENABLED = os.getenv('ML_API_ENABLED', 'True') == 'True'
    
    # Device Configuration
    PAIRING_CODE_LENGTH = 6
    PAIRING_CODE_EXPIRY_MINUTES = 15
    HEARTBEAT_INTERVAL_SECONDS = 120  # 2 minutes
    
    # Fall Detection
    FALL_CANCELLATION_WINDOW_SECONDS = 20
    FALL_ESCALATION_WINDOW_MINUTES = 5
    ML_CONFIDENCE_THRESHOLD = 0.85
    
    # Data Retention
    SENSOR_DATA_RETENTION_DAYS = 7
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        required = []
        
        if not Config.FIREBASE_CREDENTIALS_PATH:
            required.append('FIREBASE_CREDENTIALS_PATH')
            
        if required:
            print(f"⚠️  Warning: Missing configuration: {', '.join(required)}")
            print("Some features may not work properly.")
            return False
        return True
