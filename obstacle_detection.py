import cv2
import numpy as np

thres = 0.5 
nms_threshold = 0.2 

classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0/127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def detect_obstacles(img):
    classIds, confs, bbox = net.detect(img, confThreshold=0.3)
    bbox = list(bbox)
    confs = list(np.array(confs).reshape(1, -1)[0])
    confs = list(map(float, confs))

    indices = cv2.dnn.NMSBoxes(bbox, confs, 0.5, 0.2)
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

            cv2.rectangle(img, (x, y), (x + w, h + y), color=(0, 255, 0), thickness=2)
            cv2.putText(img, annotation_text, (box[0] + 10, box[1] + 30),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.circle(img, centroid, 5, (0, 0, 255), -1)  # Drawing the centroid as a red circle

        cv2.rectangle(img, (0, ROI_Y_START), (img.shape[1], ROI_Y_START + SCAN_ZONE_HEIGHT), color=(255, 0, 0), thickness=2)


    return detected_objects, centroids, img