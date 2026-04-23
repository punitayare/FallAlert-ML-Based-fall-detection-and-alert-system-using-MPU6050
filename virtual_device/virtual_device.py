"""
Virtual Device Simulator for Fall Detection System
Simulates MPU6050 sensor data, falls, battery levels, and device heartbeats
"""

import requests
import time
import random
import math
import json
from datetime import datetime
from typing import Dict, List

class VirtualDevice:
    """Simulates a wearable device with MPU6050 sensor"""
    
    def __init__(self, device_id: str, pairing_code: str, user_id: str, backend_url: str = "http://localhost:5000"):
        self.device_id = device_id
        self.pairing_code = pairing_code
        self.user_id = user_id
        self.backend_url = backend_url
        self.battery_level = 100
        self.is_paired = False
        self.activity_state = "standing"  # standing, walking, sitting, falling
        self.last_heartbeat = time.time()
        self.last_sensor_data_sent = time.time()
        
        # MPU6050 sensor baseline values (when stationary)
        self.baseline_accel = {"x": 0.0, "y": 0.0, "z": 9.81}  # Z-axis = gravity
        self.baseline_gyro = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        print(f"✓ Virtual device initialized: {device_id}")
        print(f"  Pairing Code: {pairing_code}")
        print(f"  User ID: {user_id}")
    
    def pair_device(self) -> bool:
        """Pair the device with the backend using pairing code"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/devices/pair",
                json={
                    "deviceId": self.device_id,
                    "pairingCode": self.pairing_code,
                    "userId": self.user_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.is_paired = True
                    print(f"✓ Device paired successfully")
                    return True
            
            print(f"✗ Pairing failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"✗ Pairing error: {e}")
            return False
    
    def generate_normal_sensor_data(self) -> Dict:
        """Generate realistic sensor data for normal activities"""
        
        # Add small random variations to simulate natural movement
        noise_accel = 0.1
        noise_gyro = 0.05
        
        if self.activity_state == "standing":
            # Minimal movement, mostly gravity on Z-axis
            accel = {
                "x": random.uniform(-noise_accel, noise_accel),
                "y": random.uniform(-noise_accel, noise_accel),
                "z": 9.81 + random.uniform(-noise_accel, noise_accel)
            }
            gyro = {
                "x": random.uniform(-noise_gyro, noise_gyro),
                "y": random.uniform(-noise_gyro, noise_gyro),
                "z": random.uniform(-noise_gyro, noise_gyro)
            }
        
        elif self.activity_state == "walking":
            # Rhythmic movement pattern (simulate steps)
            t = time.time()
            step_freq = 2.0  # 2 steps per second
            
            accel = {
                "x": 1.5 * math.sin(2 * math.pi * step_freq * t) + random.uniform(-0.3, 0.3),
                "y": 0.8 * math.cos(2 * math.pi * step_freq * t) + random.uniform(-0.2, 0.2),
                "z": 9.81 + 1.2 * math.sin(2 * math.pi * step_freq * t) + random.uniform(-0.3, 0.3)
            }
            gyro = {
                "x": 0.3 * math.sin(2 * math.pi * step_freq * t) + random.uniform(-0.1, 0.1),
                "y": 0.2 * math.cos(2 * math.pi * step_freq * t) + random.uniform(-0.1, 0.1),
                "z": 0.1 * math.sin(2 * math.pi * step_freq * t) + random.uniform(-0.05, 0.05)
            }
        
        elif self.activity_state == "sitting":
            # Very minimal movement
            accel = {
                "x": random.uniform(-0.05, 0.05),
                "y": random.uniform(-0.05, 0.05),
                "z": 9.81 + random.uniform(-0.05, 0.05)
            }
            gyro = {
                "x": random.uniform(-0.02, 0.02),
                "y": random.uniform(-0.02, 0.02),
                "z": random.uniform(-0.02, 0.02)
            }
        
        else:  # Default to standing
            accel = self.baseline_accel.copy()
            gyro = self.baseline_gyro.copy()
        
        return {
            "deviceId": self.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "accelerometer": accel,
            "gyroscope": gyro,
            "batteryLevel": self.battery_level,
            "status": "online"
        }
    
    def generate_fall_sensor_data(self) -> List[Dict]:
        """Generate sensor data sequence for a fall event"""
        
        fall_sequence = []
        
        # Phase 1: Sudden acceleration (freefall detection)
        for i in range(3):
            fall_sequence.append({
                "deviceId": self.device_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "accelerometer": {
                    "x": random.uniform(-2.0, 2.0),
                    "y": random.uniform(-2.0, 2.0),
                    "z": random.uniform(0.5, 3.0)  # Reduced gravity during freefall
                },
                "gyroscope": {
                    "x": random.uniform(-3.0, 3.0),
                    "y": random.uniform(-3.0, 3.0),
                    "z": random.uniform(-3.0, 3.0)
                },
                "batteryLevel": self.battery_level,
                "status": "online"
            })
            time.sleep(0.1)
        
        # Phase 2: Impact (high acceleration spike)
        for i in range(2):
            fall_sequence.append({
                "deviceId": self.device_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "accelerometer": {
                    "x": random.uniform(-25.0, 25.0),
                    "y": random.uniform(-25.0, 25.0),
                    "z": random.uniform(-25.0, 25.0)
                },
                "gyroscope": {
                    "x": random.uniform(-5.0, 5.0),
                    "y": random.uniform(-5.0, 5.0),
                    "z": random.uniform(-5.0, 5.0)
                },
                "batteryLevel": self.battery_level,
                "status": "online"
            })
            time.sleep(0.1)
        
        # Phase 3: Post-impact (motionless or minimal movement)
        for i in range(5):
            fall_sequence.append({
                "deviceId": self.device_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "accelerometer": {
                    "x": random.uniform(-0.5, 0.5),
                    "y": random.uniform(-0.5, 0.5),
                    "z": random.uniform(8.0, 10.0)  # Lying down position
                },
                "gyroscope": {
                    "x": random.uniform(-0.1, 0.1),
                    "y": random.uniform(-0.1, 0.1),
                    "z": random.uniform(-0.1, 0.1)
                },
                "batteryLevel": self.battery_level,
                "status": "online"
            })
            time.sleep(0.1)
        
        return fall_sequence
    
    def send_sensor_data(self, sensor_data: Dict) -> bool:
        """Send sensor data to backend"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/sensor-data",
                json=sensor_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"✗ Failed to send data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending data: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send periodic heartbeat to keep device status updated"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/devices/heartbeat",
                json={
                    "deviceId": self.device_id,
                    "batteryLevel": self.battery_level,
                    "status": "online"
                },
                timeout=10
            )
            
            self.last_heartbeat = time.time()
            
            if response.status_code == 200:
                return True
            else:
                print(f"✗ Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Heartbeat error: {e}")
            return False
    
    def decrease_battery(self):
        """Simulate gradual battery decrease"""
        # Decrease 0.5% per hour (realistic for wearable device)
        decrease_rate = 0.5 / 3600  # Per second
        self.battery_level = max(0, self.battery_level - decrease_rate)
    
    def simulate_fall(self):
        """Simulate a fall event"""
        print(f"\n⚠️  SIMULATING FALL EVENT at {datetime.now().strftime('%H:%M:%S')}")
        
        self.activity_state = "falling"
        fall_data = self.generate_fall_sensor_data()
        
        # Send fall sequence data
        for data_point in fall_data:
            self.send_sensor_data(data_point)
        
        print(f"✓ Fall sequence sent ({len(fall_data)} data points)")
        
        # Return to standing after fall
        time.sleep(2)
        self.activity_state = "standing"
    
    def run(self, duration: int = 300, fall_probability: float = 0.05):
        """
        Run the virtual device simulation
        
        Args:
            duration: Simulation duration in seconds (default 5 minutes)
            fall_probability: Probability of fall per minute (default 5%)
        """
        
        print(f"\n{'='*60}")
        print(f"Starting Virtual Device Simulation")
        print(f"{'='*60}")
        print(f"Duration: {duration} seconds ({duration/60:.1f} minutes)")
        print(f"Fall Probability: {fall_probability*100:.1f}% per minute")
        print(f"Backend URL: {self.backend_url}")
        print(f"{'='*60}\n")
        
        # Try to pair device first
        if not self.is_paired:
            print("Attempting to pair device...")
            self.pair_device()
        
        start_time = time.time()
        iteration = 0
        
        try:
            while time.time() - start_time < duration:
                iteration += 1
                
                # Send heartbeat every 2 minutes (updates device status)
                if time.time() - self.last_heartbeat >= 120:
                    print(f"\n💓 Sending heartbeat (Battery: {self.battery_level:.1f}%)")
                    self.send_heartbeat()
                
                # Random activity changes
                if random.random() < 0.1:  # 10% chance per cycle
                    activities = ["standing", "walking", "sitting"]
                    new_activity = random.choice(activities)
                    if new_activity != self.activity_state:
                        self.activity_state = new_activity
                        print(f"🚶 Activity changed to: {self.activity_state}")
                
                # Random fall simulation
                if random.random() < (fall_probability / 60):  # Convert per-minute to per-second
                    self.simulate_fall()
                
                # Send sensor data only every 30 seconds (instead of every second)
                # This reduces Firebase writes from 3600/hour to 120/hour per device
                if time.time() - self.last_sensor_data_sent >= 30:
                    sensor_data = self.generate_normal_sensor_data()
                    self.send_sensor_data(sensor_data)
                    self.last_sensor_data_sent = time.time()
                
                # Decrease battery
                self.decrease_battery()
                
                # Progress indicator every 10 seconds
                if iteration % 10 == 0:
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    print(f"⏱️  Running... {elapsed:.0f}s elapsed, {remaining:.0f}s remaining (Battery: {self.battery_level:.1f}%)")
                
                # Check every second but only send data periodically
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulation interrupted by user")
        
        print(f"\n{'='*60}")
        print(f"Simulation Complete")
        print(f"{'='*60}")
        print(f"Total Duration: {time.time() - start_time:.1f} seconds")
        print(f"Final Battery Level: {self.battery_level:.1f}%")
        print(f"{'='*60}\n")


def main():
    """Main entry point for virtual device simulator"""
    
    print("\n" + "="*60)
    print("Fall Detection System - Virtual Device Simulator")
    print("="*60 + "\n")
    
    # Get device information from user
    print("Enter device information:")
    device_id = input("Device ID (e.g., device_abc123): ").strip()
    pairing_code = input("Pairing Code (6 digits): ").strip()
    user_id = input("User ID: ").strip()
    
    # Optional: backend URL
    backend_url = input("Backend URL (default: http://localhost:5000): ").strip()
    if not backend_url:
        backend_url = "http://localhost:5000"
    
    # Simulation parameters
    duration_input = input("Simulation duration in minutes (default: 5): ").strip()
    duration = int(duration_input) * 60 if duration_input else 300
    
    fall_prob_input = input("Fall probability per minute (0-1, default: 0.05): ").strip()
    fall_probability = float(fall_prob_input) if fall_prob_input else 0.05
    
    # Create and run virtual device
    device = VirtualDevice(device_id, pairing_code, user_id, backend_url)
    device.run(duration, fall_probability)


if __name__ == "__main__":
    main()
