// lib/services/notification_service.dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('📩 Background message: ${message.notification?.title}');
}

class NotificationService {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  // Initialize everything
  static Future<void> initialize() async {
    // Request permission
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Initialize local notifications
    const AndroidInitializationSettings androidInit =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initSettings =
        InitializationSettings(android: androidInit);

    await _localNotifications.initialize(initSettings);

    // Get FCM token
    String? token = await _messaging.getToken();
    print('✓ FCM Token: $token');

    // Handle foreground messages (visible notifications)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📩 Foreground message: ${message.notification?.title}');

      // Display a local notification
      if (message.notification != null) {
        showLocalNotification(message);
      }
    });

    // Handle background messages
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  }

  // Display a local notification for foreground messages
  static Future<void> showLocalNotification(RemoteMessage message) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      'default_channel_id',
      'General Notifications',
      channelDescription: 'This channel is used for general notifications.',
      importance: Importance.max,
      priority: Priority.high,
      showWhen: true,
    );

    const NotificationDetails notificationDetails =
        NotificationDetails(android: androidDetails);

    await _localNotifications.show(
      message.hashCode,
      message.notification?.title ?? 'No title',
      message.notification?.body ?? 'No body',
      notificationDetails,
    );
  }

  static Future<String?> getToken() => _messaging.getToken();
}
