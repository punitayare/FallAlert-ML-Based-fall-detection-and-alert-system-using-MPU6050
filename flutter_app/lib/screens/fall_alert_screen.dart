// lib/screens/fall_alert_screen.dart
import 'package:flutter/material.dart';
import '../models/fall_event.dart';

class FallAlertScreen extends StatefulWidget {
  final FallEvent event;

  const FallAlertScreen({super.key, required this.event});

  @override
  State<FallAlertScreen> createState() => _FallAlertScreenState();
}

class _FallAlertScreenState extends State<FallAlertScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fall Alert'),
        backgroundColor: widget.event.isCritical ? Colors.red : Colors.orange,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: widget.event.isCritical ? Colors.red.shade50 : Colors.orange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(
                      Icons.warning,
                      size: 80,
                      color: widget.event.isCritical ? Colors.red : Colors.orange,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      widget.event.isCritical ? 'CRITICAL FALL DETECTED!' : 'Fall Detected',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: widget.event.isCritical ? Colors.red : Colors.orange,
                      ),
                    ),
                    const SizedBox(height: 8),
                   
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Event Details',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Divider(),
                    _buildDetailRow('Device', widget.event.deviceId),
                    _buildDetailRow('Time', _formatLocalTime(widget.event.timestamp)),
                    _buildDetailRow('Severity', widget.event.severity.toUpperCase()),
                    _buildDetailRow('Detection Method', widget.event.detectionMethod),
                    _buildDetailRow('Status', widget.event.status),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Sensor Data',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Divider(),
                    const Text('Accelerometer:'),
                    _buildDetailRow('  X', '${widget.event.accelerometer['x']?.toStringAsFixed(2)} m/s²'),
                    _buildDetailRow('  Y', '${widget.event.accelerometer['y']?.toStringAsFixed(2)} m/s²'),
                    _buildDetailRow('  Z', '${widget.event.accelerometer['z']?.toStringAsFixed(2)} m/s²'),
                    const SizedBox(height: 8),
                    const Text('Gyroscope:'),
                    _buildDetailRow('  X', '${widget.event.gyroscope['x']?.toStringAsFixed(2)} rad/s'),
                    _buildDetailRow('  Y', '${widget.event.gyroscope['y']?.toStringAsFixed(2)} rad/s'),
                    _buildDetailRow('  Z', '${widget.event.gyroscope['z']?.toStringAsFixed(2)} rad/s'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (widget.event.isActive) ...[
              ElevatedButton(
                onPressed: () {
                  // TODO: Implement emergency call
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Emergency Call'),
                      content: const Text('This feature will call emergency services.\n\nComing soon!'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('OK'),
                        ),
                      ],
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.red,
                ),
                child: const Text(
                  'Call Emergency Services',
                  style: TextStyle(fontSize: 16, color: Colors.white),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatLocalTime(DateTime utcTime) {
    // Convert UTC to local time
    final localTime = utcTime.toLocal();
    return localTime.toString().substring(0, 19);
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.grey),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
