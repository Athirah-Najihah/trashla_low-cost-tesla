import cv2
import time
import numpy as np
import configparser
from path_finding import PathFinder, detect_qr_code
from obstacle_detection import detect_obstacles
from datetime import datetime
from telegram import Bot
from robot_control import (get_garbage_level, close_serial, stop_robot, move_robot_left, move_robot_right, 
                           move_robot_forward, turn_left_at_junction, turn_right_at_junction, move_backward)

# Initialize cameras
cap_path = cv2.VideoCapture(1)  # Camera for path finding
cap_obstacle = cv2.VideoCapture(0)  # Camera for obstacle detection

# Constants for frame dimensions
FRAME_WIDTH = 640
FRAME_CENTER_X = FRAME_WIDTH // 2

# States
WAITING = 0
STANDBY = 1
FULL_MODE = 2
NAVIGATING_PATH = 3
REACHED_END = 4

# Starting state
state = WAITING

# Initialize the PathFinder
pathfinder = PathFinder()

# Load Telegram configurations from the config file
config = configparser.ConfigParser()
config.read('config.txt')

TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')

# Variable to remember wall turn direction
wall_turn_direction = None

# Threshold for garbage level (in cm). Adjust this value based on the requirements.
GARBAGE_THRESHOLD = 10

previous_commands = []


def send_telegram_notification():
    try:
        location = "FK Level 1"
        bot = Bot(token=TOKEN)
        current_time = datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
        message = f"‼️ Garbage Disposal Alert ‼️\nLocation: {location}\nDatetime: {current_time}\nPlease empty the bin."
        bot.sendMessage(chat_id=CHAT_ID, text=message)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error while sending message: {e}")

while True:
    garbage_level = get_garbage_level()
    # garbage_level = 9

    if garbage_level is not None:
        if state == WAITING and garbage_level >= GARBAGE_THRESHOLD:
            print("Garbage level below threshold. Entering STANDBY mode.")
            state = STANDBY
        elif state == STANDBY and garbage_level < GARBAGE_THRESHOLD:
            print("Garbage level above threshold. Entering FULL_MODE.")
            state = FULL_MODE
        elif state == FULL_MODE and garbage_level >= GARBAGE_THRESHOLD:
            print("Garbage level below threshold. Returning to STANDBY mode.")
            state = STANDBY

    ret_path, frame_path = cap_path.read()
    ret_obstacle, frame_obstacle = cap_obstacle.read()

    if state == STANDBY:
        print("Robot in STANDBY mode. Waiting for garbage level to rise.")

    elif state == FULL_MODE:
        print("Garbage level above threshold. Starting journey.")
        state = NAVIGATING_PATH

    elif state == NAVIGATING_PATH:
        qr_code_data = detect_qr_code(frame_path)

        if qr_code_data:
            print(f"QR Code Detected: {qr_code_data}. Pausing for a moment...")
            time.sleep(1)  # Pause for 5 seconds
        
        if qr_code_data == "END":
            print("Detected END QR code! Stopping journey.")
            stop_robot()
            state = REACHED_END
            send_telegram_notification()
            break

        if qr_code_data in ["TURN_LEFT_AT_JUNCTION", "TURN_RIGHT_AT_JUNCTION", "FORWARD"]:
            print(f"Detected QR Code: {qr_code_data}")
            if qr_code_data == "TURN_LEFT_AT_JUNCTION":
                turn_left_at_junction()
            elif qr_code_data == "TURN_RIGHT_AT_JUNCTION":
                turn_right_at_junction()
            elif qr_code_data == "FORWARD":
                move_robot_forward()
            continue  # Move to the next frame
        
        direction, cx, cy, frame_path = pathfinder.path_finder(frame_path)

        if direction == "FACE_WALL":
            if not wall_turn_direction:
                wall_turn_direction = "LEFT" if np.random.choice([True, False]) else "RIGHT"

            # Reverse first
            move_backward()
            time.sleep(1)  # Adjust the sleep time based on your robot's dynamics
            
            if wall_turn_direction == "LEFT":
                move_robot_left()
            else:
                move_robot_right()
            time.sleep(1)
            continue
        else:
            wall_turn_direction = None  # Reset wall turn direction when not facing a wall

        if direction == "LEFT":
            move_robot_left()
        elif direction == "RIGHT":
            move_robot_right()
        else:  # This caters to both "ON_TRACK" and "UNKNOWN" scenarios
            move_robot_forward()
                
    # Process Obstacle Detection
    if state == NAVIGATING_PATH:
        obstacles, obstacle_centroids, frame_obstacle_processed = detect_obstacles(frame_obstacle)
        if obstacles:
            print("Obstacles detected in ROI:", obstacles)
            stop_robot()
            if len(obstacle_centroids) > 0:
                avg_centroid_x = sum([c[0] for c in obstacle_centroids]) / len(obstacle_centroids)
                if avg_centroid_x < FRAME_CENTER_X:
                    move_robot_right()
                else:
                    move_robot_left()

    # Display results
    cv2.imshow("Corridor Following", frame_path)
    cv2.imshow("Obstacle Detection", frame_obstacle_processed)

    if cv2.waitKey(500) & 0xFF == ord('q'):
        break

cap_path.release()
cap_obstacle.release()
cv2.destroyAllWindows()
close_serial()  # Close the serial connection