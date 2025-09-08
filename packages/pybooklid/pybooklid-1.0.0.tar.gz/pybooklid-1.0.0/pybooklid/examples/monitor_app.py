#!/usr/bin/env python3
"""
Advanced monitoring application with statistics and logging.
"""

import sys
import os
import time
import statistics
from datetime import datetime
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from macbook_lid import LidSensor, LidSensorError

class LidAngleMonitor:
    """Advanced lid angle monitor with statistics and logging."""
    
    def __init__(self, history_size: int = 100):
        self.sensor = LidSensor()
        self.history = deque(maxlen=history_size)
        self.start_time = time.time()
        self.total_readings = 0
        self.last_angle = None
        
    def log_reading(self, angle: float):
        """Log a new angle reading with statistics."""
        now = time.time()
        self.history.append({
            'angle': angle,
            'timestamp': now,
            'change': angle - self.last_angle if self.last_angle else 0
        })
        self.total_readings += 1
        self.last_angle = angle
    
    def get_statistics(self) -> dict:
        """Calculate current statistics."""
        if not self.history:
            return {}
        
        angles = [r['angle'] for r in self.history]
        changes = [abs(r['change']) for r in self.history if r['change'] != 0]
        
        runtime = time.time() - self.start_time
        
        return {
            'runtime_seconds': runtime,
            'total_readings': self.total_readings,
            'readings_per_second': self.total_readings / runtime if runtime > 0 else 0,
            'current_angle': self.last_angle,
            'min_angle': min(angles),
            'max_angle': max(angles),
            'mean_angle': statistics.mean(angles),
            'angle_range': max(angles) - min(angles),
            'movements': len(changes),
            'avg_movement': statistics.mean(changes) if changes else 0,
            'max_movement': max(changes) if changes else 0,
        }
    
    def detect_state(self, angle: float) -> str:
        """Detect lid state based on angle."""
        if angle < 15:
            return "CLOSED"
        elif angle < 45:
            return "SLIGHTLY_OPEN" 
        elif angle < 90:
            return "HALF_OPEN"
        elif angle < 135:
            return "MOSTLY_OPEN"
        else:
            return "FULLY_OPEN"
    
    def display_status(self):
        """Display current status and statistics."""
        stats = self.get_statistics()
        if not stats:
            return
        
        angle = stats['current_angle']
        state = self.detect_state(angle)
        
        # Clear screen and show status
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 MacBook Lid Angle Monitor")
        print("=" * 50)
        print(f"📐 Current Angle: {angle:6.1f}°")
        print(f"📱 Lid State: {state}")
        
        # Visual representation
        bar_length = int(angle / 180 * 40)
        bar = '█' * bar_length + '░' * (40 - bar_length)
        print(f"📊 Visual: [{bar}]")
        
        print("\n📈 Statistics:")
        print(f"   Runtime: {stats['runtime_seconds']:.1f}s")
        print(f"   Readings: {stats['total_readings']} ({stats['readings_per_second']:.1f}/s)")
        print(f"   Range: {stats['min_angle']:.1f}° - {stats['max_angle']:.1f}° (span: {stats['angle_range']:.1f}°)")
        print(f"   Average: {stats['mean_angle']:.1f}°")
        print(f"   Movements: {stats['movements']} (avg: {stats['avg_movement']:.1f}°, max: {stats['max_movement']:.1f}°)")
        
        print("\n💡 Press Ctrl+C to stop monitoring")
    
    def run(self, interval: float = 0.1, display_interval: int = 10):
        """Run the monitoring application."""
        print("Starting MacBook lid angle monitor...")
        
        try:
            reading_count = 0
            for angle in self.sensor.monitor(interval=interval):
                self.log_reading(angle)
                reading_count += 1
                
                # Update display periodically
                if reading_count % display_interval == 0:
                    self.display_status()
                    
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
        except LidSensorError as e:
            print(f"Sensor error: {e}")
        finally:
            self.sensor.disconnect()
            self.show_final_report()
    
    def show_final_report(self):
        """Show final statistics report."""
        stats = self.get_statistics()
        if not stats:
            print("No data collected.")
            return
        
        print("\n" + "=" * 50)
        print("📊 Final Report")
        print("=" * 50)
        print(f"Total runtime: {stats['runtime_seconds']:.1f} seconds")
        print(f"Total readings: {stats['total_readings']}")
        print(f"Average rate: {stats['readings_per_second']:.1f} readings/second")
        print(f"Angle range: {stats['min_angle']:.1f}° to {stats['max_angle']:.1f}°")
        print(f"Total movements: {stats['movements']}")
        print(f"Average movement: {stats['avg_movement']:.1f}°")
        print(f"Largest movement: {stats['max_movement']:.1f}°")
        
        # Save data if requested
        save = input("\nSave data to CSV file? (y/N): ").lower().startswith('y')
        if save:
            self.save_to_csv()
    
    def save_to_csv(self):
        """Save collected data to CSV file."""
        if not self.history:
            print("No data to save.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lid_angle_data_{timestamp}.csv"
        
        try:
            with open(filename, 'w') as f:
                f.write("timestamp,angle,change,state\n")
                for reading in self.history:
                    state = self.detect_state(reading['angle'])
                    f.write(f"{reading['timestamp']:.3f},{reading['angle']:.1f},{reading['change']:.1f},{state}\n")
            
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save data: {e}")

def main():
    """Run the monitoring application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MacBook Lid Angle Monitor")
    parser.add_argument('--interval', type=float, default=0.1, 
                       help='Reading interval in seconds (default: 0.1)')
    parser.add_argument('--history', type=int, default=500,
                       help='Number of readings to keep in history (default: 500)')
    parser.add_argument('--display-rate', type=int, default=5,
                       help='Display update rate (every N readings, default: 5)')
    
    args = parser.parse_args()
    
    monitor = LidAngleMonitor(history_size=args.history)
    monitor.run(interval=args.interval, display_interval=args.display_rate)

if __name__ == "__main__":
    main()