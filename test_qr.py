# test_qr.py

import cv2
from path_finding import detect_qr_code
from telegram_util import send_telegram_notification  # Import send_telegram_notification function

cap = cv2.VideoCapture(1)
ct = 0

while True:
    ret, frame = cap.read()
    cv2.imshow("Frame", frame)

    data = detect_qr_code(frame)
        
    if data == "END":  # Simulate detection of "END" QR code
        print("Detected END QR code! Triggering message sending...")
        send_telegram_notification()  # Call send_telegram_notification function
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()