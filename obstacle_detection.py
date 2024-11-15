import cv2
import numpy as np
import csv

# Set thresholds
thres = 0.5 
nms_threshold = 0.2 

# Load class names
classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

# Load model
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0/127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Initialize environment type and logging
environment_type = "narrow"  # Default environment
ground_truth_objects = []
data_logger = open('precision_recall_data.csv', mode='w', newline='')
csv_writer = csv.writer(data_logger)
csv_writer.writerow(['Frame', 'Environment', 'TP', 'FP', 'FN', 'Precision', 'Recall'])

frame_count = 0

def set_environment_type(key):
    """Switch environment based on key press."""
    global environment_type, ground_truth_objects

    print(f"                                                                Pressed key: {key} | Current Environment: {environment_type}")
    
    if key == ord('n'):

        environment_type = "narrow"
        print(f"                                                                Current Environment: {environment_type}")
        ground_truth_objects = ["door"]
    elif key == ord('o'):
        environment_type = "open"
        print(f"                                                                Current Environment: {environment_type}")

        ground_truth_objects = ["door", "couch", "chair", "potted plant", "person"]

def detect_obstacles(img):
    """Detect obstacles and return detected objects and centroids."""
    global frame_count
    classIds, confs, bbox = net.detect(img, confThreshold=thres)
    bbox = list(bbox)
    confs = list(np.array(confs).reshape(1, -1)[0])
    confs = list(map(float, confs))

    indices = cv2.dnn.NMSBoxes(bbox, confs, thres, nms_threshold)
    detected_objects = []
    centroids = []

    SCAN_ZONE_HEIGHT = 300
    ROI_Y_START = 200

    for i in indices:
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]

        box_width = w
        centroid = (x + w//2, y + h//2)  # compute the centroid

        if ROI_Y_START <= centroid[1] <= ROI_Y_START + SCAN_ZONE_HEIGHT and box_width > 130:
            detected_object = classNames[classIds[i]-1].upper()
            annotation_text = f"{detected_object} ({box_width}px)"
            # print(annotation_text)
            detected_objects.append(detected_object)
            centroids.append(centroid)

            # Draw bounding box and centroid on the image
            cv2.rectangle(img, (x, y), (x + w, h + y), color=(0, 255, 0), thickness=2)
            cv2.putText(img, annotation_text, (box[0] + 10, box[1] + 30),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.circle(img, centroid, 5, (0, 0, 255), -1)  # Drawing the centroid as a red circle

        cv2.rectangle(img, (0, ROI_Y_START), (img.shape[1], ROI_Y_START + SCAN_ZONE_HEIGHT), color=(255, 0, 0), thickness=2)

    # Log results to CSV
    evaluate_and_log(detected_objects)

    return detected_objects, centroids, img

def evaluate_and_log(detected_objects):
    """Evaluate TP, FP, FN and log precision-recall data."""
    tp = len([obj for obj in detected_objects if obj in ground_truth_objects])
    fp = len([obj for obj in detected_objects if obj not in ground_truth_objects])
    fn = len([obj for obj in ground_truth_objects if obj not in detected_objects])
    
    # Calculate precision and recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    frame_count += 1

    # Log to CSV
    csv_writer.writerow([frame_count, environment_type, tp, fp, fn, precision, recall])

# Close CSV when program ends
def close_logger():
    data_logger.close()