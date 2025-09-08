"""
PyBookLid - MacBook Lid Angle Sensor Module

A Python module for reading MacBook lid angle sensor data on macOS.
Based on reverse engineering of the IOKit HID sensor interface.

Usage:
    from pybooklid import LidSensor
    
    # One-shot reading
    sensor = LidSensor()
    angle = sensor.read_angle()
    print(f"Current angle: {angle}°")
    
    # Continuous monitoring
    for angle in sensor.monitor(interval=0.1):
        print(f"Angle: {angle:.1f}°")
        if angle < 30:  # Nearly closed
            break
"""

import os
import sys
import time
import threading
from typing import Optional, Iterator, Callable

# Set DYLD_LIBRARY_PATH for hidapi to work properly on macOS
if sys.platform == 'darwin':
    homebrew_lib = '/opt/homebrew/lib'
    if os.path.exists(homebrew_lib):
        current_dyld = os.environ.get('DYLD_LIBRARY_PATH', '')
        if homebrew_lib not in current_dyld:
            os.environ['DYLD_LIBRARY_PATH'] = f"{homebrew_lib}:{current_dyld}" if current_dyld else homebrew_lib

try:
    import hid
except ImportError:
    raise ImportError(
        "hidapi package is required. Install with: pip install hidapi"
    )

# Hardware constants from reverse engineering
VENDOR_ID = 0x05AC      # Apple
PRODUCT_ID = 0x8104     # MacBook sensor hub
USAGE_PAGE = 0x0020     # HID Sensor page
USAGE = 0x008A          # Orientation sensor
FEATURE_REPORT_ID = 1   # Feature report containing angle data

class LidSensorError(Exception):
    """Base exception for lid sensor errors."""
    pass

class LidSensor:
    """
    MacBook lid angle sensor interface.
    
    Provides access to the MacBook's built-in lid angle sensor through
    the HID interface. The sensor reports angles in degrees, typically
    ranging from ~0° (closed) to ~180° (fully open).
    """
    
    def __init__(self, auto_connect: bool = True):
        """
        Initialize the lid sensor.
        
        Args:
            auto_connect: If True, automatically find and connect to the sensor
        
        Raises:
            LidSensorError: If sensor cannot be found or opened
        """
        self.device = None
        self._device_path = None
        
        if auto_connect:
            self.connect()
    
    def connect(self) -> bool:
        """
        Find and connect to the lid angle sensor.
        
        Returns:
            True if successfully connected, False otherwise
        
        Raises:
            LidSensorError: If no sensor found or connection fails
        """
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        
        for dev_info in devices:
            if (dev_info.get('usage_page') == USAGE_PAGE and 
                dev_info.get('usage') == USAGE):
                
                self._device_path = dev_info['path']
                if isinstance(self._device_path, bytes):
                    self._device_path = self._device_path.decode('utf-8')
                
                try:
                    self.device = hid.device()
                    self.device.open_path(self._device_path.encode('utf-8'))
                    
                    # Verify the device works
                    if self._test_connection():
                        return True
                    else:
                        self.disconnect()
                        
                except Exception as e:
                    if self.device:
                        self.disconnect()
                    continue
        
        raise LidSensorError(
            "MacBook lid angle sensor not found. "
            "This may not be supported on your MacBook model."
        )
    
    def _test_connection(self) -> bool:
        """Test if we can read data from the connected device."""
        try:
            data = self.device.get_feature_report(FEATURE_REPORT_ID, 8)
            return data is not None and len(data) >= 3
        except Exception:
            return False
    
    def disconnect(self):
        """Disconnect from the sensor."""
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None
    
    def is_connected(self) -> bool:
        """Check if the sensor is currently connected."""
        return self.device is not None
    
    def read_angle(self) -> Optional[float]:
        """
        Read the current lid angle.
        
        Returns:
            Angle in degrees (0-180), or None if reading fails
            
        Raises:
            LidSensorError: If sensor not connected
        """
        if not self.device:
            raise LidSensorError("Sensor not connected. Call connect() first.")
        
        try:
            # Read feature report containing angle data
            data = self.device.get_feature_report(FEATURE_REPORT_ID, 8)
            
            if data and len(data) >= 3:
                # Data format: [report_id, angle_low_byte, angle_high_byte, ...]
                # Skip report ID and combine low/high bytes
                angle_low = data[1]
                angle_high = data[2]
                raw_angle = (angle_high << 8) | angle_low
                
                return float(raw_angle)
        except Exception as e:
            # Don't raise on read errors, just return None
            pass
        
        return None
    
    def monitor(self, 
                interval: float = 0.1, 
                callback: Optional[Callable[[float], None]] = None,
                max_duration: Optional[float] = None) -> Iterator[float]:
        """
        Continuously monitor lid angle changes.
        
        Args:
            interval: Update interval in seconds (default: 0.1)
            callback: Optional callback function called with each angle reading
            max_duration: Maximum monitoring duration in seconds (None = infinite)
        
        Yields:
            Current angle in degrees
            
        Example:
            for angle in sensor.monitor(interval=0.2):
                print(f"Angle: {angle:.1f}°")
                if angle < 10:  # Stop when nearly closed
                    break
        """
        if not self.device:
            raise LidSensorError("Sensor not connected. Call connect() first.")
        
        start_time = time.time()
        last_angle = None
        
        try:
            while True:
                # Check duration limit
                if max_duration and (time.time() - start_time) >= max_duration:
                    break
                
                angle = self.read_angle()
                
                if angle is not None:
                    # Only yield/callback on actual changes or first reading
                    if angle != last_angle:
                        if callback:
                            callback(angle)
                        yield angle
                        last_angle = angle
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            # Allow clean exit on Ctrl+C
            pass
    
    def wait_for_change(self, 
                       threshold: float = 1.0, 
                       timeout: Optional[float] = None) -> Optional[float]:
        """
        Wait for the lid angle to change by at least the threshold amount.
        
        Args:
            threshold: Minimum change in degrees to detect (default: 1.0)
            timeout: Maximum wait time in seconds (None = no timeout)
        
        Returns:
            New angle when change detected, or None if timeout
        """
        if not self.device:
            raise LidSensorError("Sensor not connected. Call connect() first.")
        
        initial_angle = self.read_angle()
        if initial_angle is None:
            return None
        
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time) >= timeout:
                return None
            
            current_angle = self.read_angle()
            if current_angle is not None:
                if abs(current_angle - initial_angle) >= threshold:
                    return current_angle
            
            time.sleep(0.05)  # Check frequently for responsiveness
    
    def __enter__(self):
        """Context manager entry."""
        if not self.device:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()

# Convenience functions for quick access
def read_lid_angle() -> Optional[float]:
    """
    Quick one-shot lid angle reading.
    
    Returns:
        Current lid angle in degrees, or None if sensor unavailable
    """
    try:
        with LidSensor() as sensor:
            return sensor.read_angle()
    except LidSensorError:
        return None

def is_sensor_available() -> bool:
    """
    Check if the lid angle sensor is available on this MacBook.
    
    Returns:
        True if sensor can be accessed, False otherwise
    """
    try:
        with LidSensor() as sensor:
            return sensor.read_angle() is not None
    except LidSensorError:
        return False