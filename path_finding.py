import cv2
import numpy as np
from pyzbar.pyzbar import decode
import time
import csv

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
        self.total_frames = 0
        self.on_track_count = 0
        self.qr_code_detected_count = 0
        self.start_time = time.time()  # Start time for FPS calculation
        self.csv_file = open('pathfinding_metrics.csv', mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Frame', 'Direction', 'Center_X', 'Center_Y', 'QR Code Detected', 'FPS', 'Centroid Error'])

    def path_finder(self, frame, wall_turn_direction):
        self.total_frames += 1
        frame_start_time = time.time()  # To measure processing time per frame

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
        if total_edge_pixels < 0.2 * height * width:
            direction = "FACE_WALL"
        else:
            direction = "UNKNOWN"
            wall_roi = None

        qr_code_data = detect_qr_code(roi)
        print(f"QR Code Data: {qr_code_data}")  # Debugging line
        if qr_code_data:
            self.qr_code_detected_count += 1
            print("QR Code Detected:", qr_code_data)  # Debugging line
            print("Logging QR Code to CSV")  # Debugging line
            self.csv_writer.writerow([self.total_frames, 'QR_CODE_DETECTED', -1, -1, qr_code_data, 'N/A'])
            if qr_code_data in ["TURN_LEFT_AT_JUNCTION", "TURN_RIGHT_AT_JUNCTION", "FORWARD"]:
                return qr_code_data, -1, -1, frame


        lines = cv2.HoughLinesP(edged, 1, np.pi / 180, 10, minLineLength=5, maxLineGap=10)

        direction = "UNKNOWN"
        cx, cy = -1, -1

        if lines is not None:
            centroids = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1 + roi_start_y), (x2, y2 + roi_start_y), (0, 255, 0), 2)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + roi_start_y
                centroids.append((mx, my))

            cx_current = int(np.mean([x for x, y in centroids]))
            cy_current = int(np.mean([y for x, y in centroids]))

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

            cx = int(np.mean([x for x, y in self.past_centroids]))
            cy = int(np.mean([y for x, y in self.past_centroids]))

            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            FRAME_CENTER_X = FRAME_WIDTH // 2
            MARGIN = 70  # Adjust as needed

            if (FRAME_CENTER_X - MARGIN) < cx < (FRAME_CENTER_X + MARGIN):
                direction = "ON_TRACK"
                self.on_track_count += 1
            elif cx < (FRAME_CENTER_X - MARGIN):
                direction = "LEFT"
            else:
                direction = "RIGHT"

            cv2.line(frame, (FRAME_CENTER_X, 0), (FRAME_CENTER_X, frame.shape[0]), (0, 255, 0), 2)
            cv2.line(frame, (FRAME_CENTER_X - MARGIN, 0), (FRAME_CENTER_X - MARGIN, frame.shape[0]), (0, 0, 255), 2)
            cv2.line(frame, (FRAME_CENTER_X + MARGIN, 0), (FRAME_CENTER_X + MARGIN, frame.shape[0]), (0, 0, 255), 2)

            cv2.circle(frame, (cx, frame.shape[0] // 2), 10, (255, 0, 0), -1)

        # Calculate FPS (frames per second)
        frame_processing_time = time.time() - frame_start_time
        fps = 1 / frame_processing_time if frame_processing_time > 0 else 0

        # Log data for this frame
        centroid_error = abs(cx - FRAME_CENTER_X)
        self.csv_writer.writerow([self.total_frames, direction, cx, cy, 'N/A', round(fps, 2), centroid_error])

        return direction, cx, cy, frame, wall_roi

    def finalize(self):
        # Calculate overall pathfinding accuracy
        accuracy = (self.on_track_count / self.total_frames) * 100 if self.total_frames > 0 else 0
        total_time = time.time() - self.start_time
        average_fps = self.total_frames / total_time if total_time > 0 else 0

        print(f"Pathfinding Accuracy: {accuracy:.2f}%")
        print(f"QR Codes Detected: {self.qr_code_detected_count}")
        print(f"Average FPS: {average_fps:.2f}")

        # Close the CSV file
        self.csv_file.close()
