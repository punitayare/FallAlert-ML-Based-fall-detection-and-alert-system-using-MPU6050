# Fall Detection Mobile App

Complete Flutter mobile application for fall detection system with real-time notifications.

## Features

✅ **User Authentication** - Firebase Auth login/registration  
✅ **Device Pairing** - Pair devices using 6-digit codes  
✅ **Real-time Monitoring** - View device status and battery levels  
✅ **Fall Alerts** - Instant notifications when falls are detected  
✅ **Event History** - View past fall events with details  
✅ **False Alarm Handling** - Mark falls as false alarms  
✅ **Device Management** - View and delete paired devices  

## Setup Instructions

### Prerequisites

1. **Flutter SDK** - Install Flutter 3.0 or higher
2. **Android Studio / VS Code** with Flutter plugins
3. **Firebase Project** - Create a Firebase project for your app

### Step 1: Install Dependencies

```bash
cd flutter_app
flutter pub get
```

### Step 2: Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Add Android and/or iOS app
4. Download configuration files:
   - **Android**: `google-services.json` → `android/app/`
   - **iOS**: `GoogleService-Info.plist` → `ios/Runner/`

5. Update `lib/main.dart` to initialize Firebase:

```dart
// Uncomment this line in main.dart:
await Firebase.initializeApp();
```

### Step 3: Update API Configuration

Edit `lib/config/api_config.dart`:

```dart
// For Android Emulator:
static const String baseUrl = 'http://10.0.2.2:5000';

// For Real Device (replace with your computer's IP):
static const String baseUrl = 'http://172.20.10.3:5000';

// For Production:
static const String baseUrl = 'https://your-backend.com';
```

### Step 4: Run the App

```bash
# Check connected devices
flutter devices

# Run on connected device
flutter run

# Run on specific device
flutter run -d <device-id>

# Build APK
flutter build apk --release
```

## Project Structure

```
lib/
├── main.dart                  # Entry point
├── config/
│   └── api_config.dart       # API endpoints configuration
├── models/
│   ├── device.dart           # Device data model
│   ├── fall_event.dart       # Fall event data model
│   └── user.dart             # User data model
├── services/
│   ├── api_service.dart      # Backend API calls
│   ├── auth_service.dart     # Firebase authentication
│   └── notification_service.dart # Push notifications
└── screens/
    ├── splash_screen.dart    # Splash screen
    ├── login_screen.dart     # Login page
    ├── register_screen.dart  # Registration page
    ├── home_screen.dart      # Main dashboard
    ├── pair_device_screen.dart # Device pairing
    ├── device_details_screen.dart # Device info
    └── fall_alert_screen.dart # Fall event details
```

## Backend Integration

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/devices` | GET | Get user's devices |
| `/api/devices/pair` | POST | Pair a device |
| `/api/devices/{id}` | DELETE | Delete device |
| `/api/fall-events` | GET | Get fall events |
| `/api/fall-events/{id}/cancel` | POST | Dismiss fall alert |

### Authentication

The app uses **Firebase Authentication** for user management. Users must be registered in Firebase Auth to access the app.

## Features by Screen

### 1. Login Screen
- Email and password authentication
- Form validation
- Navigate to registration
- Auto-navigate to home if already logged in

### 2. Register Screen
- User registration with Firebase
- Collect: name, email, phone, password
- Password confirmation
- Navigate to home after registration

### 3. Home Screen
- **Summary Cards**: Device count, active alerts
- **Device List**: All paired devices with status
- **Recent Events**: Last 5 fall events
- **Pull to Refresh**: Update data
- **Floating Action Button**: Pair new device

### 4. Pair Device Screen
- Enter device ID and 6-digit pairing code
- Form validation
- Success/error feedback
- Instructions card

### 5. Device Details Screen
- Device information
- Battery level
- Last seen timestamp
- Fall event history for device
- Delete device option

### 6. Fall Alert Screen
- Event details display
- Sensor data (accelerometer, gyroscope)
- Confidence percentage
- Severity level
- **"I'm OK"** button to dismiss
- Emergency call option (placeholder)

## Notifications

The app uses both **Firebase Cloud Messaging (FCM)** and **Local Notifications**.

### Setup FCM

1. Add `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
2. Notifications are auto-initialized in `main.dart`
3. Falls trigger push notifications

### Notification Types

- **Fall Detected**: When ML model detects a fall
- **Device Offline**: When device disconnects (future)
- **Low Battery**: When battery < 20% (future)

## Testing

### Test with Virtual Device Simulator

1. Start backend server:
```bash
cd backend
.\venv\Scripts\python.exe app.py
```

2. Start ML API (optional):
```bash
cd ml_api
python app.py
```

3. Run virtual device:
```bash
cd virtual_device
..\.venv\Scripts\python.exe run_simulator.py device_test 123456 <userId>
```

4. In mobile app:
   - Register/Login
   - Pair device using `device_test` and code `123456`
   - Wait for fall simulation
   - Receive notification

## Troubleshooting

### "Unable to connect to backend"

**Solution**: Check API URL in `api_config.dart`
- Android Emulator: Use `10.0.2.2` instead of `localhost`
- Real Device: Use computer's IP address
- Ensure backend is running and accessible

### "Firebase not initialized"

**Solution**:
1. Add `google-services.json` to `android/app/`
2. Uncomment Firebase initialization in `main.dart`
3. Run `flutter clean` and `flutter pub get`

### "No notifications received"

**Solution**:
1. Check notification permissions in device settings
2. Ensure FCM token is being generated (check console logs)
3. Verify backend is sending FCM messages

### "Device pairing fails"

**Solution**:
1. Verify device exists in web dashboard
2. Check pairing code is correct (6 digits)
3. Ensure device is not already paired
4. Check backend logs for errors

## Building for Production

### Android

```bash
# Build APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### iOS

```bash
# Build IPA
flutter build ios --release

# Open in Xcode for signing
open ios/Runner.xcworkspace
```

## Environment-Specific Builds

Create different configurations for dev/staging/production:

```dart
// lib/config/environment.dart
class Environment {
  static const String apiUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://10.0.2.2:5000',
  );
}

// Build with environment variable:
flutter run --dart-define=API_URL=https://production-api.com
```

## Security Considerations

1. **API Keys**: Don't commit Firebase config files to public repos
2. **SSL/TLS**: Use HTTPS for production API
3. **Token Storage**: Uses secure SharedPreferences
4. **Authentication**: Firebase Auth handles security
5. **Input Validation**: All forms validated

## Performance Optimization

- **Lazy Loading**: Devices and events load on demand
- **Caching**: User ID cached locally
- **Pull to Refresh**: Manual data refresh
- **Efficient Rendering**: Using ListView.builder
- **Image Optimization**: Using built-in icons

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Offline mode with local database
- [ ] Emergency contacts management
- [ ] Call emergency services integration
- [ ] Device location on map
- [ ] Historical analytics and charts
- [ ] Multi-language support
- [ ] Dark mode theme

## Support

For issues or questions:
- Check backend logs: `backend/app.py`
- Check app logs: `flutter logs`
- Verify API connectivity: Test endpoints with Postman

## License

This project is part of the Fall Detection System.
