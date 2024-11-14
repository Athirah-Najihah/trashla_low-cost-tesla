import cv2

def main():
    # Open the first camera (usually the default camera)
    cap1 = cv2.VideoCapture(0)
    # Open the second camera (change the index if you have multiple cameras)
    cap2 = cv2.VideoCapture(2)

    if not cap1.isOpened() or not cap2.isOpened():
        print("Error: Could not open one or both cameras.")
        return

    while True:
        # Capture frame-by-frame from the first camera
        ret1, frame1 = cap1.read()
        if not ret1:
            print("Error: Could not read frame from camera 1.")
            break

        # Capture frame-by-frame from the second camera
        ret2, frame2 = cap2.read()
        if not ret2:
            print("Error: Could not read frame from camera 2.")
            break

        # Display the resulting frames in separate windows
        cv2.imshow('Camera 1', frame1)
        cv2.imshow('Camera 2', frame2)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close windows
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
