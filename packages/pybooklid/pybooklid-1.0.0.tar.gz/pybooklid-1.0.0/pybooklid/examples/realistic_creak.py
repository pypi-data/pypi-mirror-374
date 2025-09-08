#!/usr/bin/env python3
"""
Realistic Wood Creak Sound Generator

Creates organic, wood-like door creak sounds instead of harsh electronic tones.
Uses multiple oscillators, filtered noise, and realistic amplitude envelopes.
"""

import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import numpy as np
    import sounddevice as sd
    from scipy import signal
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  Audio libraries not available. Install with:")
    print("   pip install numpy sounddevice scipy")

from macbook_lid import LidSensor

class RealisticCreakGenerator:
    """Generates realistic wood door creak sounds."""
    
    def __init__(self):
        self.sample_rate = 44100
        self.buffer_size = 2048
        
        # Pre-calculate filter coefficients for wood resonance
        self.wood_filters = self._create_wood_filters()
        
    def _create_wood_filters(self):
        """Create bandpass filters that simulate wood resonances."""
        filters = []
        
        # Wood typically has resonances at these frequencies
        wood_resonances = [150, 280, 420, 680, 1100]
        
        for freq in wood_resonances:
            # Create bandpass filter
            sos = signal.butter(2, [freq * 0.8, freq * 1.2], 
                               btype='bandpass', fs=self.sample_rate, output='sos')
            filters.append(sos)
        
        return filters
    
    def _apply_wood_resonance(self, audio_signal):
        """Apply wood-like resonance filtering to audio."""
        result = np.zeros_like(audio_signal)
        
        for i, sos in enumerate(self.wood_filters):
            # Filter the signal
            filtered = signal.sosfilt(sos, audio_signal)
            
            # Mix with different weights (lower frequencies stronger)
            weight = 1.0 / (i + 1) ** 0.7
            result += filtered * weight
        
        return result
    
    def _generate_organic_noise(self, duration, base_freq):
        """Generate organic, wood-like noise instead of white noise."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Multiple noise sources at different frequencies
        noise = np.zeros(samples)
        
        # Low frequency rumble (wood fiber movement)
        noise += 0.3 * np.random.normal(0, 1, samples)
        
        # Medium frequency scratching (surface friction)
        high_freq_noise = np.random.normal(0, 1, samples)
        # Low-pass filter for more organic sound
        b, a = signal.butter(3, 800, fs=self.sample_rate)
        high_freq_noise = signal.filtfilt(b, a, high_freq_noise)
        noise += 0.2 * high_freq_noise
        
        # Add some periodic components (regular wood grain)
        grain_freq = base_freq * 0.3
        noise += 0.1 * np.sin(2 * np.pi * grain_freq * t + np.random.random() * 2 * np.pi)
        
        return noise
    
    def generate_wood_creak(self, angle: float, speed: float, direction: int, duration: float = 0.3):
        """Generate realistic wood door creak sound."""
        if not AUDIO_AVAILABLE or speed < 1.0:
            return
        
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Base frequency depends on angle (different parts of hinge)
        base_freq = 60 + 40 * math.sin(angle * math.pi / 180 * 2.5)
        
        # Speed affects multiple characteristics
        speed_factor = min(speed / 15.0, 1.0)
        intensity = 0.15 * speed_factor
        
        # Create multiple sound components
        
        # 1. Main creak tone (fundamental frequency)
        main_tone = intensity * 0.4 * np.sin(2 * np.pi * base_freq * t)
        
        # 2. Harmonic overtones (not pure harmonics for realism)
        overtone1 = intensity * 0.2 * np.sin(2 * np.pi * base_freq * 1.618 * t)  # Golden ratio
        overtone2 = intensity * 0.15 * np.sin(2 * np.pi * base_freq * 2.414 * t)  # Sqrt(2) * sqrt(3)
        
        # 3. Organic noise component
        organic_noise = self._generate_organic_noise(duration, base_freq)
        organic_noise *= intensity * 0.6
        
        # 4. Combine all components
        signal_raw = main_tone + overtone1 + overtone2 + organic_noise
        
        # 5. Apply wood resonance filtering
        signal_filtered = self._apply_wood_resonance(signal_raw)
        
        # 6. Create realistic amplitude envelope
        # Wood creaks have a sharp attack but longer, irregular decay
        attack_time = duration * 0.1
        decay_time = duration * 0.9
        
        envelope = np.ones(samples)
        
        # Sharp attack
        attack_samples = int(attack_time * self.sample_rate)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Irregular decay (like wood settling)
        decay_samples = samples - attack_samples
        if decay_samples > 0:
            # Create irregular decay with some fluctuations
            decay_base = np.exp(-np.linspace(0, 3, decay_samples))
            decay_flutter = 1 + 0.3 * np.sin(np.linspace(0, 8 * np.pi, decay_samples))
            envelope[attack_samples:] = decay_base * decay_flutter
        
        # Apply envelope
        final_signal = signal_filtered * envelope
        
        # 7. Direction-specific characteristics
        if direction < 0:  # Closing - slightly more pressure, lower pitch
            final_signal *= 1.2
            # Slight pitch bend down
            pitch_bend = np.linspace(1.0, 0.95, samples)
            final_signal = np.interp(np.arange(samples) / pitch_bend, 
                                   np.arange(samples), final_signal)
        else:  # Opening - slightly brighter
            # Add a tiny bit more high frequency content
            high_freq_component = 0.05 * intensity * np.sin(2 * np.pi * base_freq * 3 * t)
            final_signal += high_freq_component * envelope
        
        # 8. Final processing
        # Soft clipping to avoid harsh digital distortion
        final_signal = np.tanh(final_signal * 2) * 0.3
        
        # Play the sound
        try:
            sd.play(final_signal, self.sample_rate, blocking=False)
        except Exception as e:
            print(f"Audio error: {e}")

def run_realistic_creaky_door():
    """Run the realistic creaky door with proper wood sounds."""
    print("🚪 Realistic Wood Door Creak")
    print("=" * 40)
    
    if not AUDIO_AVAILABLE:
        print("❌ Audio libraries required. Install with:")
        print("   pip install numpy sounddevice scipy")
        return
    
    print("Move your MacBook lid to hear realistic wood door creaks!")
    print("Press Ctrl+C to stop\n")
    
    creak_gen = RealisticCreakGenerator()
    
    try:
        with LidSensor() as sensor:
            last_angle = None
            last_time = time.time()
            sound_cooldown = 0
            
            for angle in sensor.monitor(interval=0.03):  # Higher resolution
                current_time = time.time()
                dt = current_time - last_time
                
                if last_angle is not None:
                    angle_change = angle - last_angle
                    speed = abs(angle_change) / dt if dt > 0 else 0
                    direction = 1 if angle_change > 0 else -1
                    
                    # Visual feedback
                    if abs(angle_change) > 0.3:  # Movement threshold
                        direction_text = "🟢 OPENING" if angle_change > 0 else "🔴 CLOSING"
                        
                        # Different intensity visualization
                        if speed > 15:
                            intensity_icon = "🔥🔥🔥"  # Very fast
                        elif speed > 8:
                            intensity_icon = "🔥🔥"    # Fast
                        elif speed > 3:
                            intensity_icon = "🔥"      # Medium
                        else:
                            intensity_icon = "💫"      # Slow
                        
                        # Position bar
                        bar_length = int(angle / 180 * 25)
                        bar = '█' * bar_length + '░' * (25 - bar_length)
                        
                        print(f"\r🚪 {angle:6.1f}° [{bar}] {direction_text} {speed:4.1f}°/s {intensity_icon}", 
                              end='', flush=True)
                        
                        # Generate realistic creak sound
                        if sound_cooldown <= 0 and speed > 1.5:
                            creak_gen.generate_wood_creak(angle, speed, direction)
                            # Cooldown prevents audio overlap
                            sound_cooldown = max(5, int(20 / speed))  # Adaptive cooldown
                    else:
                        # Show position when still
                        bar_length = int(angle / 180 * 25)
                        bar = '█' * bar_length + '░' * (25 - bar_length)
                        print(f"\r🚪 {angle:6.1f}° [{bar}] (still)                              ", 
                              end='', flush=True)
                
                last_angle = angle
                last_time = current_time
                sound_cooldown = max(0, sound_cooldown - 1)
                
    except KeyboardInterrupt:
        print("\n\n🔇 Wood creak stopped!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def demo_realistic_sounds():
    """Demo different creak sounds at various speeds and positions."""
    if not AUDIO_AVAILABLE:
        print("Audio libraries required")
        return
    
    print("🎵 Realistic Wood Creak Demo")
    print("Testing different angles and speeds...\n")
    
    creak_gen = RealisticCreakGenerator()
    
    # Test different scenarios
    scenarios = [
        (30, 5, 1, "Slow opening from closed"),
        (45, 12, 1, "Medium speed opening"),
        (90, 20, 1, "Fast opening at middle"),
        (120, 8, -1, "Medium closing from open"),
        (60, 25, -1, "Fast closing slam"),
        (150, 3, 1, "Very slow near fully open"),
    ]
    
    for angle, speed, direction, description in scenarios:
        print(f"🚪 {description} ({angle}°, {speed}°/s)")
        creak_gen.generate_wood_creak(angle, speed, direction, duration=0.8)
        time.sleep(1.5)
    
    print("\n✅ Realistic sound demo complete")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Realistic Wood Creak Effect")
    parser.add_argument('--demo', action='store_true',
                       help='Demo realistic creak sounds')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_realistic_sounds()
    else:
        run_realistic_creaky_door()

if __name__ == "__main__":
    main()