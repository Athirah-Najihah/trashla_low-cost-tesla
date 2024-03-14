import serial
import time

# Add this before the try block in get_garbage_level
import collections


last_sent_time = int(round(time.time() * 1000))
override_last_sent_time = int(round(time.time() * 51000))
qr_override_last_sent_time = int(round(time.time() * 1000))

# Initialize a deque to store the last N readings
distance_buffer = collections.deque(maxlen=5)

ser = serial.Serial('COM10', 115200)

# Wait for the serial connection to stabilize
time.sleep(2)

# Flush the input and output buffers
ser.flushInput()
ser.flushOutput()

# def override_robot(command):
#     try:
#         ser.write((command + '\n').encode('utf-8'))
#         print("OVERRRIDDINGGGGG THE ROBOTTTTTTTTTTTTTTTTTTTTTTTT: ", command)

#     except Exception as e:
#         print(f"Error sending command: {e}")

def send_command(command):
    global last_sent_time
    current_time = int(round(time.time() * 1000))
    if current_time - last_sent_time >= 3500:  # 3000 milliseconds = 3 seconds
        try:
            ser.write((command + '\n').encode('utf-8'))
            print("COMMAND SENT: ", command)
            last_sent_time = current_time
        except Exception as e:
            print(f"Error sending command: {e}")

def override_robot(command):
    global override_last_sent_time
    override_current_time = int(round(time.time() * 1000))
    if override_current_time - override_last_sent_time >= 1000:  # 3000 milliseconds = 3 seconds
        try:
            ser.write((command + '\n').encode('utf-8'))
            print("OVERRIDING THE ROBOT with command: ", command)  
            override_last_sent_time = override_current_time
        except Exception as e:
            print(f"Error sending command: {e}")

def qr_override_robot(command):
    global qr_override_last_sent_time
    qr_override_current_time = int(round(time.time() * 1000))
    if qr_override_current_time - qr_override_last_sent_time >= 1000:  # 3000 milliseconds = 3 seconds
        try:
            ser.write((command + '\n').encode('utf-8'))
            print("QR OVERRIDING THE ROBOT with command: ", command)  
            qr_override_last_sent_time = qr_override_current_time
        except Exception as e:
            print(f"Error sending command: {e}")


def stop_robot(override):
    cmd = "STOP\n"

    if not override:
        print("Stopping Robot")
        send_command(cmd)
    else:
        print("Stopping Robot (Override)")
        override_robot(cmd)

def move_robot_left(override):
    cmd = "LEFT\n"
    if not override:
        print("Moving Left")
        send_command(cmd)
    else:
        print("Moving Left (Override)")
        override_robot(cmd)

def move_robot_right(override):
    cmd = "RIGHT\n"
    if not override:
        print("Moving Right")
        send_command(cmd)
    else:
        print("Moving Right(Override)")
        override_robot(cmd)

def avoid_obs_right(override):
    cmd = "STRAFE_RIGHT\n"
    if not override:
        print("STRAFE Right")
        send_command(cmd)
    else:
        print("STRAFE Right(Override)")
        override_robot(cmd)

def avoid_obs_left(override):
    cmd = "STRAFE_LEFT\n"
    if not override:
        print("STRAFE Left")
        send_command(cmd)
    else:
        print("STRAFE Left(Override)")
        override_robot(cmd)


def move_robot_forward(override):
    cmd = "FORWARD\n"

    if not override:
        print("Moving forward")
        send_command(cmd)
    else:
        print("Moving forward(Override)")
        override_robot(cmd)

def turn_left_at_junction(override):
    cmd = "TURN_LEFT_AT_JUNCTION\n"
    
    if not override:
        print("TURN_LEFT_AT_JUNCTION")
        send_command(cmd)
    else:
        print("TURN_LEFT_AT_JUNCTION(Override)")
        qr_override_robot(cmd)

    

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