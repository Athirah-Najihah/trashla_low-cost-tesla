"""
import serial
import time

ser = serial.Serial('COM10', 9600)

def get_garbage_level():
    -
    Read the distance data from the ultrasonic sensor connected to Arduino.
    Returns the distance in cm.
    -
    try:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Distance: "):
                distance = line.split(":")[1]
                return float(distance)
        else:
            return None
    except Exception as e:
        print(f"Error reading distance: {e}")
        return None

def close_serial():
    ser.close()
"""