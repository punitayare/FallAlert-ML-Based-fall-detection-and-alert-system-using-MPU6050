// lib/models/fall_event.dart
import 'package:intl/intl.dart';

class FallEvent {
  final String id;
  final String deviceId;
  final DateTime timestamp;
  final Map<String, double> accelerometer;
  final Map<String, double> gyroscope;
 
  final String severity; // low, moderate, high, critical
  final String detectionMethod; // ml_api, rule_based
  final String status; // detected, confirmed, false_alarm, resolved
  final bool notified;
  final DateTime? cancelledAt;

  FallEvent({
    required this.id,
    required this.deviceId,
    required this.timestamp,
    required this.accelerometer,
    required this.gyroscope,
    
    required this.severity,
    required this.detectionMethod,
    required this.status,
    required this.notified,
    this.cancelledAt,
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

  factory FallEvent.fromJson(Map<String, dynamic> json) {
    return FallEvent(
      id: json['id'] ?? '',
      deviceId: json['deviceId'] ?? '',
      timestamp: _parseDate(json['timestamp']) ?? DateTime.now(),
      accelerometer: {
        'x': (json['accelerometer']?['x'] ?? 0).toDouble(),
        'y': (json['accelerometer']?['y'] ?? 0).toDouble(),
        'z': (json['accelerometer']?['z'] ?? 0).toDouble(),
      },
      gyroscope: {
        'x': (json['gyroscope']?['x'] ?? 0).toDouble(),
        'y': (json['gyroscope']?['y'] ?? 0).toDouble(),
        'z': (json['gyroscope']?['z'] ?? 0).toDouble(),
      },
    
      severity: json['severity'] ?? 'unknown',
      detectionMethod: json['detection_method'] ?? json['detectionMethod'] ?? 'unknown',
      status: json['status'] ?? 'detected',
      notified: json['notified'] ?? false,
      cancelledAt: _parseDate(json['cancelledAt']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'deviceId': deviceId,
      'timestamp': timestamp.toIso8601String(),
      'accelerometer': accelerometer,
      'gyroscope': gyroscope,
      'severity': severity,
      'detection_method': detectionMethod,
      'status': status,
      'notified': notified,
      'cancelledAt': cancelledAt?.toIso8601String(),
    };
  }

  bool get isCritical => severity == 'critical' || severity == 'high';
  bool get isActive => status == 'detected' || status == 'confirmed';
  bool get isFalseAlarm => status == 'false_alarm';
}
