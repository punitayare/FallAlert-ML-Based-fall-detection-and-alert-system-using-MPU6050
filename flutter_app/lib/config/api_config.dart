// lib/config/api_config.dart
class ApiConfig {
  // ⚠️ Backend URL - Using your PC's local IP for wireless debugging
  // Your PC IP: 192.168.29.120 (on same network as phone)
  static const String baseUrl = 'http://192.168.137.102:5000';
  
  // API Endpoints
  static const String loginEndpoint = '/api/auth/login';
  static const String registerEndpoint = '/api/users/create';
  static const String devicesEndpoint = '/api/devices';
  static const String pairDeviceEndpoint = '/api/devices/pair';
  static const String sensorDataEndpoint = '/api/sensor-data';
  static const String fallEventsEndpoint = '/api/fall-events';
  
  // WebSocket
  static const String websocketUrl = 'ws://192.168.137.102:5000';
  
  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 10);
  
  // Headers
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Get full URL
  static String getUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }
}
