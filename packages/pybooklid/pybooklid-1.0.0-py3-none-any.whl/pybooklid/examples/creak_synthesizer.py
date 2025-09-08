#!/usr/bin/env python3
"""
Adaptive Door Creak Sound Synthesizer

Generates realistic door creak sounds that adapt to lid movement speed and angle.
The sound changes based on:
- Movement speed (faster = louder, higher frequency)
- Angle (different creaks for different positions)
- Direction (opening vs closing)
"""

import numpy as np
import sounddevice as sd
import time
import threading
import math
from typing import Optional, Callable
from dataclasses import dataclass
from macbook_lid import LidSensor

@dataclass
class CreakParameters:
    """Parameters for creak sound synthesis."""
    base_frequency: float = 120.0      # Base creak frequency (Hz)
    frequency_range: float = 200.0     # Frequency variation range
    amplitude: float = 0.3             # Base amplitude
    noise_level: float = 0.4           # Amount of noise/texture
    resonance: float = 0.7             # Resonant filtering
    attack_time: float = 0.1           # Sound attack time
    decay_time: float = 0.3            # Sound decay time

class AdaptiveCreakSynthesizer:
    """Real-time adaptive creak sound synthesizer."""
    
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_playing = False
        self.audio_thread = None
        self.current_params = CreakParameters()
        
        # Audio generation state
        self.phase = 0.0
        self.envelope = 0.0
        self.noise_phase = 0.0
        self.filter_state = [0.0, 0.0]  # Simple 2-pole filter state
        
        # Movement tracking
        self.last_angle = None
        self.movement_speed = 0.0
        self.movement_direction = 0  # -1: closing, 1: opening, 0: still
        
        # Audio stream
        self.stream = None
    
    def start_audio(self):
        """Start the audio output stream."""
        if self.stream is not None:
            return
        
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.buffer_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            self.stream.start()
            print("🔊 Audio creak synthesizer started")
        except Exception as e:
            print(f"Failed to start audio: {e}")
    
    def stop_audio(self):
        """Stop the audio output stream."""
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("🔇 Audio synthesizer stopped")
    
    def update_movement(self, angle: float, dt: float):
        """Update movement parameters based on new angle."""
        if self.last_angle is not None:
            # Calculate movement speed (degrees per second)
            angle_change = angle - self.last_angle
            self.movement_speed = abs(angle_change) / dt if dt > 0 else 0
            
            # Determine direction
            if abs(angle_change) > 0.5:  # Threshold to ignore noise
                self.movement_direction = 1 if angle_change > 0 else -1
            else:
                self.movement_direction = 0
        
        self.last_angle = angle
        
        # Update creak parameters based on movement
        self._update_creak_parameters(angle)
    
    def _update_creak_parameters(self, angle: float):
        """Update creak synthesis parameters based on angle and movement."""
        # Base frequency varies with angle (different "spots" on the hinge)
        angle_factor = (angle / 180.0)  # 0 to 1
        base_freq = 80 + 100 * (0.5 + 0.5 * math.sin(angle_factor * math.pi * 3))
        
        # Speed affects amplitude and frequency variation
        speed_factor = min(self.movement_speed / 20.0, 1.0)  # Normalize to 0-1
        
        # Direction affects tone character
        direction_factor = 1.0 + 0.3 * self.movement_direction
        
        # Update parameters
        self.current_params.base_frequency = base_freq * direction_factor
        self.current_params.amplitude = 0.1 + 0.4 * speed_factor
        self.current_params.frequency_range = 50 + 150 * speed_factor
        self.current_params.noise_level = 0.2 + 0.3 * speed_factor
        
        # Different resonance for opening vs closing
        if self.movement_direction > 0:  # Opening
            self.current_params.resonance = 0.6
        elif self.movement_direction < 0:  # Closing
            self.current_params.resonance = 0.8
        else:  # Still
            self.current_params.resonance = 0.9
    
    def _audio_callback(self, outdata, frames, time, status):
        """Audio callback for real-time synthesis."""
        if status:
            print(f"Audio status: {status}")
        
        # Only generate sound if there's movement
        target_envelope = self.current_params.amplitude if self.movement_speed > 0.5 else 0.0
        
        # Generate audio buffer
        buffer = np.zeros(frames, dtype=np.float32)
        
        for i in range(frames):
            # Smooth envelope changes
            self.envelope += (target_envelope - self.envelope) * 0.01
            
            if self.envelope > 0.01:
                # Primary oscillator with frequency modulation
                freq_mod = (1.0 + 0.5 * math.sin(self.noise_phase * 0.1)) * self.current_params.base_frequency
                sample = math.sin(self.phase) * self.envelope
                
                # Add noise for texture
                noise = (np.random.random() - 0.5) * 2.0 * self.current_params.noise_level
                sample += noise * self.envelope
                
                # Simple resonant filter
                self.filter_state[0] += (sample - self.filter_state[0]) * 0.1
                self.filter_state[1] += (self.filter_state[0] - self.filter_state[1]) * 0.05
                filtered_sample = self.filter_state[1] * self.current_params.resonance + sample * (1 - self.current_params.resonance)
                
                buffer[i] = np.clip(filtered_sample, -1.0, 1.0)
                
                # Update phases
                self.phase += 2.0 * math.pi * freq_mod / self.sample_rate
                if self.phase > 2.0 * math.pi:
                    self.phase -= 2.0 * math.pi
                
                self.noise_phase += 1
            else:
                buffer[i] = 0.0
        
        outdata[:, 0] = buffer

class CreakingLidMonitor:
    """Lid monitor with adaptive creak sounds."""
    
    def __init__(self):
        self.sensor = LidSensor()
        self.synthesizer = AdaptiveCreakSynthesizer()
        self.last_time = time.time()
    
    def start(self):
        """Start monitoring with creak sounds."""
        print("🚪 Starting creaking lid monitor...")
        print("Move your MacBook lid to hear adaptive door creaks!")
        print("Press Ctrl+C to stop")
        
        self.synthesizer.start_audio()
        
        try:
            for angle in self.sensor.monitor(interval=0.05):  # High update rate
                current_time = time.time()
                dt = current_time - self.last_time
                
                # Update synthesizer with new angle
                self.synthesizer.update_movement(angle, dt)
                
                # Display info
                speed = self.synthesizer.movement_speed
                direction = ["Closing", "Still", "Opening"][self.synthesizer.movement_direction + 1]
                
                # Visual feedback
                bar_length = int(angle / 180 * 30)
                bar = '█' * bar_length + '░' * (30 - bar_length)
                
                print(f"\r🚪 {angle:6.1f}° [{bar}] {direction:7s} Speed: {speed:5.1f}°/s", 
                      end='', flush=True)
                
                self.last_time = current_time
                
        except KeyboardInterrupt:
            print("\n\n🔇 Stopping creaky lid monitor...")
        finally:
            self.synthesizer.stop_audio()
            self.sensor.disconnect()

def create_sample_creak_file():
    """Create a sample static creak sound file for testing."""
    print("🎵 Creating sample creak sound file...")
    
    sample_rate = 44100
    duration = 3.0  # seconds
    samples = int(sample_rate * duration)
    
    # Generate a sample creak sound
    t = np.linspace(0, duration, samples, False)
    
    # Base frequency sweep
    freq_sweep = 120 + 80 * np.sin(t * 2 * np.pi * 0.5)
    
    # Amplitude envelope
    envelope = np.exp(-t * 2) * (1 - np.exp(-t * 10))
    
    # Generate sound
    signal = envelope * (
        np.sin(2 * np.pi * freq_sweep * t) +
        0.3 * np.sin(2 * np.pi * freq_sweep * 2 * t) +
        0.2 * np.random.normal(0, 1, samples)
    )
    
    # Simple low-pass filter
    signal = np.convolve(signal, [0.25, 0.5, 0.25], mode='same')
    
    # Save as WAV file
    try:
        import scipy.io.wavfile
        scipy.io.wavfile.write('sample_creak.wav', sample_rate, 
                              (signal * 32767).astype(np.int16))
        print("✅ Sample creak saved as 'sample_creak.wav'")
    except ImportError:
        print("⚠️  Install scipy to save WAV files: pip install scipy")

def main():
    """Main function with different modes."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptive Door Creak Synthesizer")
    parser.add_argument('--sample', action='store_true', 
                       help='Create a sample creak sound file')
    parser.add_argument('--test-audio', action='store_true',
                       help='Test audio system')
    
    args = parser.parse_args()
    
    if args.sample:
        create_sample_creak_file()
        return
    
    if args.test_audio:
        print("🔊 Testing audio system...")
        synthesizer = AdaptiveCreakSynthesizer()
        synthesizer.start_audio()
        
        # Generate some test movement
        for angle in range(30, 150, 5):
            synthesizer.update_movement(angle, 0.1)
            time.sleep(0.2)
        
        time.sleep(1)
        synthesizer.stop_audio()
        print("✅ Audio test complete")
        return
    
    # Default: run the creaking lid monitor
    try:
        monitor = CreakingLidMonitor()
        monitor.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try installing audio dependencies:")
        print("   pip install sounddevice numpy")

if __name__ == "__main__":
    main()