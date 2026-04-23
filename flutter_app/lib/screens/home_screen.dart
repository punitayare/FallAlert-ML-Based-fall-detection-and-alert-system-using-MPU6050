// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../models/device.dart';
import '../models/fall_event.dart';
import 'pair_device_screen_old.dart';
import 'device_details_screen.dart';
import 'fall_alert_screen.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with WidgetsBindingObserver {

  final AuthService _authService = AuthService();

  List<Device> _devices = [];
  List<FallEvent> _events = [];

  bool _isLoading = true;
  String? _userId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _init();
  }

  Future<void> _init() async {
    _userId = await _authService.getSavedUserId();
    await _refresh();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _refresh(); // 🔥 auto refresh when app returns
    }
  }

 Future<void> _refresh() async {
  if (_userId == null) return;

  setState(() => _isLoading = true);

  final devices = await ApiService.getDevices(_userId!);
  final events = await ApiService.getAllFallEvents(_userId!); // fetch all

  setState(() {
    _devices = devices;
    _events = events; // store in local state
    _isLoading = false;
  });
}

  void _openPairScreen() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const PairDeviceScreen()),
    );

    _refresh(); // 🔥 refresh AFTER pairing
  }

  void _logout() async {
    await _authService.signOut();
    if (!mounted) return;

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),

      appBar: AppBar(
        title: const Text('Fall Guardian'),
        actions: [
          IconButton(onPressed: _refresh, icon: const Icon(Icons.refresh)),
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),

      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openPairScreen,
        icon: const Icon(Icons.add),
        label: const Text("Connect Device"),
      ),

      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _refresh,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [

                  // 🔥 HEADER
                  _buildHeader(),

                  const SizedBox(height: 20),

                  // 🔥 DEVICES
                  _buildDevices(),

                  const SizedBox(height: 20),

                  // 🔥 EVENTS
                  _buildEvents(),
                ],
              ),
            ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.blue, Colors.indigo],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Welcome 👋",
            style: TextStyle(color: Colors.white70),
          ),
          const SizedBox(height: 8),
          Text(
            "Devices: ${_devices.length}",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDevices() {
    if (_devices.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              const Icon(Icons.watch, size: 50, color: Colors.grey),
              const SizedBox(height: 10),
              const Text("No devices connected"),
              const SizedBox(height: 10),
              ElevatedButton(
                onPressed: _openPairScreen,
                child: const Text("Connect Device"),
              )
            ],
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("Your Devices",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),

        ..._devices.map((d) {
          return Card(
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: d.isOnline ? Colors.green : Colors.grey,
                child: const Icon(Icons.watch, color: Colors.white),
              ),
              title: Text(d.deviceName),
              subtitle: Text("Battery: ${d.batteryLevel}%"),
              trailing: Chip(
                label: Text(d.status),
                backgroundColor:
                    d.isOnline ? Colors.green.shade100 : Colors.grey.shade300,
              ),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => DeviceDetailsScreen(device: d),
                  ),
                );
              },
            ),
          );
        }),
      ],
    );
  }

  Widget _buildEvents() {
  if (_events.isEmpty) {
    return const Text("No fall events recorded");
  }

  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      const Text(
        "Fall Events",
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
      ),
      const SizedBox(height: 10),
      ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _events.length,
        itemBuilder: (context, index) {
          final e = _events[index];
          return Card(
            color: e.isCritical ? Colors.red.shade50 : null,
            child: ListTile(
              leading: const Icon(Icons.warning, color: Colors.red),
              title: const Text("Fall Detected"),
              subtitle: Text("${e.deviceId} • ${e.timestamp.toLocal()}"),
             
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => FallAlertScreen(event: e),
                  ),
                );
              },
            ),
          );
        },
      ),
    ],
  );
}
}