import serial
import time

# Add this before the try block in get_garbage_level
import collections

# Initialize a deque to store the last N readings
distance_buffer = collections.deque(maxlen=5)

ser = serial.Serial('COM10', 115200)

# Wait for the serial connection to stabilize
time.sleep(2)

# Flush the input and output buffers
ser.flushInput()
ser.flushOutput()

def send_command(command):
    try:
        ser.write((command + '\n').encode('utf-8'))
    except Exception as e:
        print(f"Error sending command: {e}")

def stop_robot():
    print("Stopping Robot")
    send_command("STOP\n")

def move_robot_left():
    print("Moving Robot Left")
    send_command("LEFT\n")

def move_robot_right():
    print("Moving Robot Right")
    send_command("RIGHT\n")

def move_robot_forward():
    print("Moving Robot Forward")
    send_command("FORWARD\n")

def turn_left_at_junction():
    print("Turning Left at Junction")
    send_command("TURN_LEFT_AT_JUNCTION\n")

def turn_right_at_junction():
    print("Turning Right at Junction")
    send_command("TURN_RIGHT_AT_JUNCTION\n")

def move_backward():
    print("Moving Robot Backward")
    send_command("REVERSE\n")

def get_garbage_level():
    """
    Read the distance data from the ultrasonic sensor connected to Arduino.
    Returns the distance in cm.
    """
    try:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Distance: "):
                # Extract the distance value
                distance = float(line.split(":")[1])

                # Add the reading to the buffer
                distance_buffer.append(distance)

                # Use the mean of the buffer as the filtered distance
                filtered_distance = sum(distance_buffer) / len(distance_buffer)
                
                print(f"Ultrasonic Distance: {filtered_distance} cm")
                return filtered_distance
        else:
            return None
    except Exception as e:
        print(f"Error reading distance: {e}")
        return None

def close_serial():
    ser.close()