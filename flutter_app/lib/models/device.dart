// lib/models/device.dart
import 'package:intl/intl.dart';

class Device {
  final String deviceId;
  final String deviceName;
  final String userId;
  final String pairingCode;
  final bool isPaired;
  final String status; // online, offline, alerting
  final double batteryLevel;
  final DateTime createdAt;
  final DateTime? lastSeen;

  Device({
    required this.deviceId,
    required this.deviceName,
    required this.userId,
    required this.pairingCode,
    required this.isPaired,
    required this.status,
    required this.batteryLevel,
    required this.createdAt,
    this.lastSeen,
  });

  // Helper to parse various date formats
  static DateTime? _parseDate(dynamic dateValue) {
    if (dateValue == null) return null;
    
    try {
      // Try ISO 8601 format first
      return DateTime.parse(dateValue.toString());
    } catch (e) {
      try {
        // Try HTTP date format (e.g., "Tue, 21 Oct 2025 20:30:03 GMT")
        final httpFormat = DateFormat('EEE, dd MMM yyyy HH:mm:ss');
        return httpFormat.parse(dateValue.toString().replaceAll(' GMT', ''));
      } catch (e2) {
        print('Warning: Could not parse date: $dateValue');
        return DateTime.now();
      }
    }
  }

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      deviceId: json['deviceId'] ?? '',
      deviceName: json['deviceName'] ?? 'Unknown Device',
      userId: json['userId'] ?? '',
      pairingCode: json['pairingCode'] ?? '',
      isPaired: json['isPaired'] ?? false,
      status: json['status'] ?? 'offline',
      batteryLevel: (json['batteryLevel'] ?? 0).toDouble(),
      createdAt: _parseDate(json['createdAt']) ?? DateTime.now(),
      lastSeen: _parseDate(json['lastSeen']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'deviceId': deviceId,
      'deviceName': deviceName,
      'userId': userId,
      'pairingCode': pairingCode,
      'isPaired': isPaired,
      'status': status,
      'batteryLevel': batteryLevel,
      'createdAt': createdAt.toIso8601String(),
      'lastSeen': lastSeen?.toIso8601String(),
    };
  }

  bool get isOnline => status == 'online';
  bool get isAlerting => status == 'alerting';
  bool get needsCharging => batteryLevel < 20;
}
