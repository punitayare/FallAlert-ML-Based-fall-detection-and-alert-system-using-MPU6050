"""
Quick start script for Virtual Device Simulator
Pre-configured with example values for easy testing
"""

from virtual_device import VirtualDevice
import sys

def run_quick_test():
    """Run simulator with example device"""
    
    print("\n" + "="*60)
    print("Virtual Device Simulator - Quick Test Mode")
    print("="*60 + "\n")
    
    # Example device configuration
    # Replace these with actual values from your device management page
    device_id = "device_test001"
    pairing_code = "123456"  # Replace with actual pairing code
    user_id = "test_user"     # Replace with actual user ID
    backend_url = "http://192.168.137.102:5000"
    
    print("Configuration:")
    print(f"  Device ID: {device_id}")
    print(f"  Pairing Code: {pairing_code}")
    print(f"  User ID: {user_id}")
    print(f"  Backend URL: {backend_url}")
    print(f"\n⚠️  NOTE: Update these values in run_simulator.py with your actual device details!\n")
    
    # Simulation settings
    duration = 300  # 5 minutes
    fall_probability = 0.2  # 20% chance per minute
    
    # Create and run device
    device = VirtualDevice(device_id, pairing_code, user_id, backend_url)
    
    print("\nSimulation Settings:")
    print(f"  Duration: {duration/60} minutes")
    print(f"  Fall Probability: {fall_probability*100}% per minute")
    print(f"\nPress Ctrl+C to stop the simulation\n")
    
    try:
        device.run(duration, fall_probability)
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation stopped by user")
        sys.exit(0)


def run_with_custom_params():
    """Run simulator with custom parameters from command line"""
    
    if len(sys.argv) < 4:
        print("\nUsage: python run_simulator.py <device_id> <pairing_code> <user_id> [backend_url]")
        print("\nExample:")
        print("  python run_simulator.py device_abc123 770773 user_xyz456")
        print("  python run_simulator.py device_abc123 770773 user_xyz456 http://localhost:5000")
        sys.exit(1)
    
    device_id = sys.argv[1]
    pairing_code = sys.argv[2]
    user_id = sys.argv[3]
    backend_url = sys.argv[4] if len(sys.argv) > 4 else "http://localhost:5000"
    
    print("\n" + "="*60)
    print("Virtual Device Simulator - Custom Mode")
    print("="*60 + "\n")
    print(f"Device ID: {device_id}")
    print(f"Pairing Code: {pairing_code}")
    print(f"User ID: {user_id}")
    print(f"Backend URL: {backend_url}\n")
    
    # Create and run device
    device = VirtualDevice(device_id, pairing_code, user_id, backend_url)
    device.run(duration=600, fall_probability=0.4)  # 10 minutes, 40% fall chance


if __name__ == "__main__":
    # If no command line args, run quick test mode
    if len(sys.argv) == 1:
        run_quick_test()
    else:
        run_with_custom_params()
