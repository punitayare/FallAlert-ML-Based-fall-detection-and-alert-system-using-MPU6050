// lib/models/user.dart
class User {
  final String userId;
  final String email;
  final String displayName;
  final String phoneNumber;
  final DateTime createdAt;

  User({
    required this.userId,
    required this.email,
    required this.displayName,
    required this.phoneNumber,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['userId'] ?? json['uid'] ?? '',
      email: json['email'] ?? '',
      displayName: json['displayName'] ?? json['name'] ?? '',
      phoneNumber: json['phoneNumber'] ?? json['phone'] ?? '',
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'email': email,
      'displayName': displayName,
      'phoneNumber': phoneNumber,
      'createdAt': createdAt.toIso8601String(),
    };
  }
}
