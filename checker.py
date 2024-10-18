import cv2
import os
import platform

def check_camera_ports():
    if platform.system() == "Linux":
        devices = [f for f in os.listdir('/dev') if f.startswith('video')]
        return [f'/dev/{device}' for device in devices]
    elif platform.system() == "Windows":
        available_cameras = []
        for i in range(10):  # Check first 10 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras
    else:
        return "Unsupported OS"

def open_cameras(camera_ports):
    caps = []
    for port in camera_ports:
        if platform.system() == "Linux":
            index = int(port.split('/')[-1].replace('video', ''))
        else:  # For Windows, already have indices
            index = port
        
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            caps.append(cap)
            print(f"Opened camera at index: {index}")
        else:
            print(f"Failed to open camera at index: {index}")
    
    return caps

def main():
    camera_ports = check_camera_ports()
    if isinstance(camera_ports, list):
        print("Available camera ports:")
        for port in camera_ports:
            print(port)

        caps = open_cameras(camera_ports)

        # Display the video feeds from opened cameras
        while caps:
            frames = []
            for cap in caps:
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                else:
                    print("Error reading frame from camera.")

            for i, frame in enumerate(frames):
                cv2.imshow(f'Camera {i}', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release all cameras
        for cap in caps:
            cap.release()
        cv2.destroyAllWindows()
    else:
        print(camera_ports)

if __name__ == "__main__":
    main()
