#!/usr/bin/env python3
"""
Creaky Door Effect - Simple example using the lid sensor with sound
"""

import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import numpy as np
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  Audio libraries not available. Install with:")
    print("   pip install numpy sounddevice")

from macbook_lid import LidSensor

class SimpleCreakGenerator:
    """Simple creak sound generator for demonstration."""
    
    def __init__(self):
        self.sample_rate = 22050  # Lower sample rate for simplicity
        self.is_playing = False
        
    def generate_creak_chunk(self, angle: float, speed: float, duration: float = 0.1):
        """Generate a small chunk of creak sound."""
        if not AUDIO_AVAILABLE:
            return
        
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Frequency based on angle (different "spots" make different sounds)
        base_freq = 80 + 40 * math.sin(angle * math.pi / 180 * 3)
        
        # Speed affects intensity and frequency variation
        speed_factor = min(speed / 10.0, 1.0)  # Normalize
        
        if speed_factor < 0.1:  # Too slow, no sound
            return
        
        # Generate the sound
        freq_variation = base_freq + 30 * speed_factor * np.sin(t * 10)
        amplitude = 0.1 * speed_factor
        
        # Main tone + harmonics + noise
        signal = (
            amplitude * np.sin(2 * np.pi * freq_variation * t) +
            amplitude * 0.3 * np.sin(2 * np.pi * freq_variation * 1.5 * t) +
            amplitude * 0.2 * np.random.normal(0, 1, samples)
        )
        
        # Simple envelope to avoid clicks
        envelope = np.linspace(1, 0.5, samples)
        signal *= envelope
        
        # Play the sound
        try:
            sd.play(signal, self.sample_rate, blocking=False)
        except Exception as e:
            print(f"Audio error: {e}")

def run_creaky_door():
    """Run the creaky door demonstration."""
    print("🚪 Creaky Door Demonstration")
    print("=" * 40)
    
    if not AUDIO_AVAILABLE:
        print("Running in silent mode (visual feedback only)")
    
    print("Move your MacBook lid to hear/see the creaky door effect!")
    print("Press Ctrl+C to stop\n")
    
    creak_gen = SimpleCreakGenerator()
    
    try:
        with LidSensor() as sensor:
            last_angle = None
            last_time = time.time()
            sound_cooldown = 0
            
            for angle in sensor.monitor(interval=0.05):
                current_time = time.time()
                dt = current_time - last_time
                
                if last_angle is not None:
                    # Calculate movement speed
                    angle_change = abs(angle - last_angle)
                    speed = angle_change / dt if dt > 0 else 0
                    
                    # Visual feedback
                    if angle_change > 0.5:  # Movement threshold
                        direction = "🔼 OPENING" if angle > last_angle else "🔽 CLOSING"
                        intensity = "🔥" * min(int(speed / 5) + 1, 5)  # Visual intensity
                        
                        print(f"\r🚪 {angle:6.1f}° {direction} Speed: {speed:5.1f}°/s {intensity:<5}", 
                              end='', flush=True)
                        
                        # Generate sound (with cooldown to avoid audio overload)
                        if AUDIO_AVAILABLE and sound_cooldown <= 0 and speed > 2:
                            creak_gen.generate_creak_chunk(angle, speed)
                            sound_cooldown = 3  # Frames to skip
                    else:
                        # Show current position when still
                        bar_length = int(angle / 180 * 20)
                        bar = '█' * bar_length + '░' * (20 - bar_length)
                        print(f"\r🚪 {angle:6.1f}° [{bar}] (still)                    ", 
                              end='', flush=True)
                
                last_angle = angle
                last_time = current_time
                sound_cooldown = max(0, sound_cooldown - 1)
                
    except KeyboardInterrupt:
        print("\n\n🔇 Creaky door stopped!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def demo_sound_only():
    """Demo the sound generation without sensor (for testing)."""
    if not AUDIO_AVAILABLE:
        print("Audio libraries required for sound demo")
        return
    
    print("🎵 Sound Generation Demo")
    print("Simulating door movement...")
    
    creak_gen = SimpleCreakGenerator()
    
    # Simulate opening the door
    for angle in range(30, 120, 5):
        speed = 8.0  # Moderate speed
        print(f"🚪 {angle:3d}° - Opening")
        creak_gen.generate_creak_chunk(angle, speed, 0.2)
        time.sleep(0.3)
    
    time.sleep(1)
    
    # Simulate closing
    for angle in range(115, 25, -7):
        speed = 12.0  # Faster closing
        print(f"🚪 {angle:3d}° - Closing")
        creak_gen.generate_creak_chunk(angle, speed, 0.15)
        time.sleep(0.25)
    
    print("✅ Sound demo complete")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Creaky Door Effect")
    parser.add_argument('--sound-only', action='store_true',
                       help='Demo sound generation without sensor')
    
    args = parser.parse_args()
    
    if args.sound_only:
        demo_sound_only()
    else:
        run_creaky_door()

if __name__ == "__main__":
    main()