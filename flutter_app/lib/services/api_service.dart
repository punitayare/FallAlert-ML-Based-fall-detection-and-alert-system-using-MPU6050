// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/device.dart';
import '../models/fall_event.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class ApiService {
  // ------------------- Firestore-based: Get devices for a user -------------------
  static Future<List<Device>> getDevices(String userId) async {
    try {
      final snapshot = await FirebaseFirestore.instance
          .collection('devices')
          .where('user_id', isEqualTo: userId)
          .get();

      return snapshot.docs.map((doc) {
        final data = doc.data();

        return Device(
          deviceId: doc.id,
          deviceName: data['device_id'] ?? doc.id,
          userId: data['user_id'] ?? userId,
          pairingCode: data['pairingCode'] ?? '',
          isPaired: true,
          status: 'online', // default online
          batteryLevel: (data['batteryLevel'] ?? 100).toDouble(),
          createdAt: (data['pairedAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
          lastSeen: (data['lastSeen'] as Timestamp?)?.toDate(),
        );
      }).toList();
    } catch (e) {
      print("❌ Error fetching devices from Firestore: $e");
      return [];
    }
  }

  // ------------------- HTTP-based: Pair a device -------------------
  static Future<Map<String, dynamic>> pairDevice({
    required String deviceId,
    required String pairingCode,
    required String userId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.getUrl(ApiConfig.pairDeviceEndpoint)),
        headers: ApiConfig.headers,
        body: json.encode({
          'deviceId': deviceId,
          'pairingCode': pairingCode,
          'userId': userId,
        }),
      ).timeout(ApiConfig.connectionTimeout);

      final data = json.decode(response.body);

      return {
        'success': data['success'] == true,
        'message': data['message'] ?? 'Unknown error',
        'device': data['device'] != null ? Device.fromJson(data['device']) : null,
      };
    } catch (e) {
      print('Error pairing device: $e');
      return {
        'success': false,
        'message': 'Connection error: $e',
      };
    }
  }

  // ------------------- HTTP-based: Get fall events -------------------
  static Future<List<FallEvent>> getFallEvents({
    String? userId,
    String? deviceId,
    int limit = 50,
  }) async {
    try {
      var url = ApiConfig.getUrl(ApiConfig.fallEventsEndpoint);
      var params = [];

      if (userId != null) params.add('userId=$userId');
      if (deviceId != null) params.add('deviceId=$deviceId');
      params.add('limit=$limit');

      if (params.isNotEmpty) {
        url += '?' + params.join('&');
      }

      final response = await http.get(
        Uri.parse(url),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          List<FallEvent> events = [];
          for (var eventJson in data['events']) {
            events.add(FallEvent.fromJson(eventJson));
          }
          return events;
        }
      }
      return [];
    } catch (e) {
      print('Error getting fall events: $e');
      return [];
    }
  }

  // ------------------- HTTP-based: Cancel/dismiss a fall event -------------------
  static Future<bool> cancelFallEvent(String eventId) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.getUrl(ApiConfig.fallEventsEndpoint)}/$eventId/cancel'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.connectionTimeout);

      final data = json.decode(response.body);
      return data['success'] == true;
    } catch (e) {
      print('Error cancelling fall event: $e');
      return false;
    }
  }
  static Stream<List<FallEvent>> streamFallEvents({
  required String deviceId,
  int limit = 5,
}) {
  return FirebaseFirestore.instance
      .collection('fall_events')
      .where('deviceId', isEqualTo: deviceId)
      .orderBy('timestamp', descending: true)
      .limit(limit)
      .snapshots()
      .map((snapshot) => snapshot.docs.map((doc) {
            final data = doc.data();
            return FallEvent.fromJson({
              'id': doc.id,
              'deviceId': data['deviceId'] ?? '',
              'userId': data['userId'] ?? '',
              'timestamp': (data['timestamp'] as Timestamp?)?.toDate(),
              'confidence': (data['confidence'] ?? 0).toDouble(),
              'status': data['status'] ?? 'detected',
              'severity': data['severity'] ?? 'high',
              'notified': data['notified'] ?? false,
            });
          }).toList());
}
  // ------------------- HTTP-based: Delete a device -------------------
  static Future<bool> deleteDevice(String deviceId) async {
    try {
      final response = await http.delete(
        Uri.parse('${ApiConfig.getUrl(ApiConfig.devicesEndpoint)}/$deviceId'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.connectionTimeout);

      final data = json.decode(response.body);
      return data['success'] == true;
    } catch (e) {
      print('Error deleting device: $e');
      return false;
    }
  }


  static Future<List<FallEvent>> getAllFallEvents(String userId, {int limit = 50}) async {
  try {
    final snapshot = await FirebaseFirestore.instance
        .collection('fall_events')
        .where('userId', isEqualTo: userId)
        .orderBy('timestamp', descending: true)
        .limit(limit) // optional, remove limit if you want all
        .get();

    return snapshot.docs.map((doc) {
      final data = doc.data();

      final timestampValue = data['timestamp'] is Timestamp
          ? (data['timestamp'] as Timestamp).toDate()
          : data['timestamp'];

      return FallEvent.fromJson({
        'id': doc.id,
        'deviceId': data['deviceId'] ?? '',
        'userId': data['userId'] ?? '',
        'timestamp': timestampValue,
        'accelerometer': data['accelerometer'] ?? {},
        'gyroscope': data['gyroscope'] ?? {},
        'confidence': (data['confidence'] ?? 0).toDouble(),
        'status': data['status'] ?? 'detected',
        'severity': data['severity'] ?? 'high',
        'detectionMethod': data['detectionMethod'] ?? 'ml_api',
        'notified': data['notified'] ?? false,
        'cancelledAt': data['cancelledAt'],
      });
    }).toList();
  } catch (e) {
    print("❌ Error fetching fall events: $e");
    return [];
  }
}
}
