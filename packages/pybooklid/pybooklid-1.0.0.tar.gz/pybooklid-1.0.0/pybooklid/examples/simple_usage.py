#!/usr/bin/env python3
"""
Simple usage examples for the MacBook lid angle sensor.
"""

try:
    from pybooklid import LidSensor, read_lid_angle, is_sensor_available
except ImportError:
    # Fallback for development/local testing
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from macbook_lid import LidSensor, read_lid_angle, is_sensor_available

def example_one_shot():
    """Example: One-shot angle reading."""
    print("=== One-shot Reading ===")
    
    angle = read_lid_angle()
    if angle is not None:
        print(f"Current lid angle: {angle:.1f}°")
    else:
        print("Sensor not available on this device")

def example_continuous_monitoring():
    """Example: Continuous monitoring with manual exit."""
    print("\n=== Continuous Monitoring ===")
    print("Move your lid, press Ctrl+C to stop")
    
    try:
        with LidSensor() as sensor:
            count = 0
            for angle in sensor.monitor(interval=0.2):
                # Visual progress bar
                bar_length = int(angle / 180 * 40)
                bar = '█' * bar_length + '░' * (40 - bar_length)
                
                print(f"\rAngle: {angle:6.1f}° [{bar}]", end='', flush=True)
                
                count += 1
                if count > 100:  # Auto-stop after 100 readings
                    break
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")

def example_gesture_detection():
    """Example: Detect opening and closing gestures."""
    print("\n=== Gesture Detection ===")
    print("Open and close your lid to see gesture detection")
    
    try:
        with LidSensor() as sensor:
            last_angle = sensor.read_angle()
            if last_angle is None:
                print("Could not get initial reading")
                return
            
            print(f"Starting angle: {last_angle:.1f}°")
            
            for angle in sensor.monitor(interval=0.1):
                diff = angle - last_angle
                
                # Detect significant movements
                if abs(diff) > 5:  # 5 degree threshold
                    if diff > 0:
                        print(f"\n🔼 Opening gesture detected: {last_angle:.1f}° → {angle:.1f}°")
                    else:
                        print(f"\n🔽 Closing gesture detected: {last_angle:.1f}° → {angle:.1f}°")
                    
                    # Check for fully closed/open
                    if angle < 10:
                        print("   → Lid is nearly closed!")
                    elif angle > 160:
                        print("   → Lid is fully open!")
                
                last_angle = angle
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")

def example_wait_for_change():
    """Example: Wait for lid movement."""
    print("\n=== Wait for Change ===")
    
    try:
        with LidSensor() as sensor:
            initial = sensor.read_angle()
            print(f"Current angle: {initial:.1f}°")
            print("Waiting for lid movement (>5° change)...")
            
            new_angle = sensor.wait_for_change(threshold=5.0, timeout=10.0)
            if new_angle:
                print(f"Movement detected! New angle: {new_angle:.1f}°")
            else:
                print("No movement detected within timeout")
                
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all examples."""
    print("MacBook Lid Angle Sensor Examples")
    print("=" * 40)
    
    # Check availability first
    if not is_sensor_available():
        print("❌ Lid angle sensor not available on this device")
        print("This may not be supported on your MacBook model.")
        return
    
    print("✅ Lid angle sensor detected")
    
    # Run examples
    example_one_shot()
    
    try:
        example_continuous_monitoring()
        example_gesture_detection()
        example_wait_for_change()
    except KeyboardInterrupt:
        print("\n\nExiting...")

if __name__ == "__main__":
    main()