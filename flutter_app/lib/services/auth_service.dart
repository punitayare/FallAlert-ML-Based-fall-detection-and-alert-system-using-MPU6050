// lib/services/auth_service.dart
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'notification_service.dart';

class AuthService {
  final firebase_auth.FirebaseAuth _auth = firebase_auth.FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Get current user
  firebase_auth.User? get currentUser => _auth.currentUser;

  // Sign in with email and password
  Future<Map<String, dynamic>> signIn(String email, String password) async {
    try {
      final credential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Save user ID
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('userId', credential.user!.uid);

      // Save FCM token
      await _saveFcmToken(credential.user!.uid);

      return {
        'success': true,
        'user': credential.user,
      };
    } on firebase_auth.FirebaseAuthException catch (e) {
      String message;
      switch (e.code) {
        case 'user-not-found':
          message = 'No user found with this email';
          break;
        case 'wrong-password':
          message = 'Wrong password';
          break;
        case 'invalid-email':
          message = 'Invalid email address';
          break;
        case 'user-disabled':
          message = 'This account has been disabled';
          break;
        default:
          message = 'Login failed: ${e.message}';
      }
      return {
        'success': false,
        'message': message,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'An error occurred: $e',
      };
    }
  }

  // Register with email and password
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String displayName,
    required String phoneNumber,
  }) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Update display name
      await credential.user!.updateDisplayName(displayName);

      // Save user ID
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('userId', credential.user!.uid);

      // Save FCM token
      await _saveFcmToken(credential.user!.uid);

      return {
        'success': true,
        'user': credential.user,
      };
    } on firebase_auth.FirebaseAuthException catch (e) {
      String message;
      switch (e.code) {
        case 'weak-password':
          message = 'Password is too weak';
          break;
        case 'email-already-in-use':
          message = 'An account already exists with this email';
          break;
        case 'invalid-email':
          message = 'Invalid email address';
          break;
        default:
          message = 'Registration failed: ${e.message}';
      }
      return {
        'success': false,
        'message': message,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'An error occurred: $e',
      };
    }
  }

  // Sign out
  Future<void> signOut() async {
    await _auth.signOut();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('userId');
  }

  // Get saved user ID
  Future<String?> getSavedUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('userId');
  }

  // Check if user is signed in
  bool isSignedIn() {
    return _auth.currentUser != null;
  }

  // Save FCM token to Firestore
  Future<void> _saveFcmToken(String userId) async {
  try {
    String? token = await NotificationService.getToken();
    if (token != null) {
      await _firestore.collection('users').doc(userId).set({
        'activeFcmToken': token, // <<--- add this
        'fcmTokens': FieldValue.arrayUnion([token]),
        'lastTokenUpdate': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
      print('✓ Active FCM token saved to Firestore');
    }
  } catch (e) {
    print('Error saving FCM token: $e');
  }
}
}
