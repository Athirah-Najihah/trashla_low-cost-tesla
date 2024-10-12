import cv2
import numpy as np
from pyzbar.pyzbar import decode

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
        # Update ROI based on the direction
        if total_edge_pixels < 0.2 * height * width:
            # Robot is facing a wall
            direction = "FACE_WALL"
            wall_roi_start_x = 0
            wall_roi_end_x = width // 2 if wall_turn_direction == "RIGHT" else width
            wall_roi = frame[:, wall_roi_start_x:wall_roi_end_x]
        else:
            # Robot is not facing a wall
            direction = "UNKNOWN"
            wall_roi = None

        qr_code_data = detect_qr_code(roi)
        if qr_code_data:
            print("QR Code Detected:", qr_code_data)
            if qr_code_data in ["TURN_LEFT_AT_JUNCTION", "TURN_RIGHT_AT_JUNCTION", "FORWARD"]:
                return qr_code_data, -1, -1, frame

        lines = cv2.HoughLinesP(edged, 1, np.pi/180, 10, minLineLength=5, maxLineGap=10)

        direction = "UNKNOWN"
        cx, cy = -1, -1

        if lines is not None:
            centroids = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Drawing the detected lines for visualization
                cv2.line(frame, (x1, y1 + roi_start_y), (x2, y2 + roi_start_y), (0, 255, 0), 2)

                mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + roi_start_y
                centroids.append((mx, my))

            # Calculate current frame's centroid
            cx_current = int(np.mean([x for x, y in centroids]))
            cy_current = int(np.mean([y for x, y in centroids]))

            # Combine it with the previous centroid with some weighting
            ALPHA = 0.7
            if self.past_centroids:
                cx_previous, cy_previous = self.past_centroids[-1]
                cx = int(ALPHA * cx_current + (1 - ALPHA) * cx_previous)
                cy = int(ALPHA * cy_current + (1 - ALPHA) * cy_previous)
            else:
                cx, cy = cx_current, cy_current

            self.past_centroids.append((cx, cy))
            if len(self.past_centroids) > 10:
                self.past_centroids.pop(0)

            # Temporal Smoothing
            cx = int(np.mean([x for x, y in self.past_centroids]))
            cy = int(np.mean([y for x, y in self.past_centroids]))

            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            FRAME_CENTER_X = FRAME_WIDTH // 2
            MARGIN = 70  # Adjust as needed

            if (FRAME_CENTER_X - MARGIN) < cx < (FRAME_CENTER_X + MARGIN):
                direction = "ON_TRACK"
            elif cx < (FRAME_CENTER_X - MARGIN):
                direction = "LEFT"
            else:
                direction = "RIGHT"

            cv2.line(frame, (FRAME_CENTER_X, 0), (FRAME_CENTER_X, frame.shape[0]), (0, 255, 0), 2)

            # Draw the margin lines
            cv2.line(frame, (FRAME_CENTER_X - MARGIN, 0), (FRAME_CENTER_X - MARGIN, frame.shape[0]), (0, 0, 255), 2)
            cv2.line(frame, (FRAME_CENTER_X + MARGIN, 0), (FRAME_CENTER_X + MARGIN, frame.shape[0]), (0, 0, 255), 2)

            # Draw the point
            cv2.circle(frame, (cx, frame.shape[0] // 2), 10, (255, 0, 0), -1)

        return direction, cx, cy, frame, wall_roi