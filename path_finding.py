import cv2
import numpy as np
from pyzbar.pyzbar import decode
import csv
import time

FRAME_WIDTH = 640

def detect_qr_code(frame):
    qr_codes = decode(frame)
    for qr_code in qr_codes:
        data = qr_code.data.decode('utf-8')
        if data in ["END", "TURN_LEFT_AT_JUNCTION", "TURN_RIGHT_AT_JUNCTION", "FORWARD"]:
            return data
    return None

class PathFinder:
    def __init__(self):
        self.past_centroids = []

        # **Added CSV setup**
        # Open or create a CSV file to log the data
        with open('centroid_accuracy_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Actual_Centroid_X', 'Ideal_Centroid_X', 'Centroid_Error'])

    def path_finder(self, frame, wall_turn_direction):
        # Set the ROI
        height, width = frame.shape[:2]
        roi_start_y = 10
        roi = frame[roi_start_y:, :]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Adaptive Canny Thresholding
        median_intensity = np.median(blurred)
        lower_threshold = int(max(0, (1.0 - 0.33) * median_intensity))
        upper_threshold = int(min(255, (1.0 + 0.33) * median_intensity))
        edged = cv2.Canny(blurred, lower_threshold, upper_threshold)

        # Check if facing a wall
        total_edge_pixels = np.sum(edged == 255)
        direction = "UNKNOWN"
        cx, cy = -1, -1

        if total_edge_pixels < 0.2 * height * width:
            # Robot is facing a wall
            direction = "FACE_WALL"
        else:
            # Detect QR codes
            qr_code_data = detect_qr_code(roi)
            if qr_code_data:
                return qr_code_data, -1, -1, frame

            # Detect lines using Hough Line Transform
            lines = cv2.HoughLinesP(edged, 1, np.pi/180, 10, minLineLength=5, maxLineGap=10)
            if lines is not None:
                centroids = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + roi_start_y
                    centroids.append((mx, my))

                cx_current = int(np.mean([x for x, y in centroids]))

                # Combine it with the previous centroid with some weighting
                ALPHA = 0.7
                if self.past_centroids:
                    cx_previous, _ = self.past_centroids[-1]
                    cx = int(ALPHA * cx_current + (1 - ALPHA) * cx_previous)
                else:
                    cx = cx_current

                self.past_centroids.append((cx, cy))
                if len(self.past_centroids) > 10:
                    self.past_centroids.pop(0)

                # Temporal Smoothing
                cx = int(np.mean([x for x, _ in self.past_centroids]))

                # **Added ideal centroid calculation**
                # Set the ideal centroid as the center of the frame
                ideal_cx = FRAME_WIDTH // 2

                # **Added centroid error calculation**
                # Calculate the centroid error as the absolute difference
                centroid_error = abs(cx - ideal_cx)

                # **Added CSV logging**
                # Log the data (timestamp, actual centroid, ideal centroid, centroid error)
                timestamp = time.time()
                with open('centroid_accuracy_data.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, cx, ideal_cx, centroid_error])

                # **(Optional) Visualization** - This helps to see the centroids on the frame
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        return direction, cx, cy, frame