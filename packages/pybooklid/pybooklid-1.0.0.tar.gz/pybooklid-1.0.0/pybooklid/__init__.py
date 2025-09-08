"""
PyBookLid - MacBook Lid Angle Sensor Library

A Python library for reading MacBook lid angle sensor data on macOS.
Provides real-time access to the built-in lid angle sensor available on modern MacBooks.
"""

from .macbook_lid import (
    LidSensor,
    LidSensorError,
    read_lid_angle,
    is_sensor_available
)

__version__ = "1.0.0"
__author__ = "tcsenpai"
__email__ = "tcsenpai@discus.sh"
__description__ = "MacBook lid angle sensor library for Python"

__all__ = [
    'LidSensor',
    'LidSensorError', 
    'read_lid_angle',
    'is_sensor_available'
]