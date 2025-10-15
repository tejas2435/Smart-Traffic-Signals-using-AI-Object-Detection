import cv2
import serial
import time
import numpy as np

# Serial setup
esp = serial.Serial('COM5', 9600)
time.sleep(2)

# IP camera URLs
cam1_url = 'http://10.205.30.206:4747/video?type=mjpeg'
cam2_url = 'http://10.205.30.202:4747/video?type=mjpeg'

# Load the model
net = cv2.dnn.readNetFromCaffe(
    r"C:\Users\tejas\Desktop\TrafficAI\MobileNetSSD_deploy.prototxt",
    r"C:\Users\tejas\Desktop\TrafficAI\MobileNetSSD_deploy.caffemodel"
)

# Classes that may include vehicles
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle",
           "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse",
           "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
VEHICLE_CLASSES = {"car", "bus", "motorbike", "bicycle", "truck"} 

# Get frame from camera
def get_frame(cap):
    ret, frame = cap.read()
    return frame if ret else None

# Detection logic (returns count & draws boxes)
def detect_vehicles(frame):
    if frame is None:
        return 0, frame
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    count = 0

    (h, w) = frame.shape[:2]

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        idx = int(detections[0, 0, i, 1])

        if confidence > 0.5:
            label = CLASSES[idx]
            if label in VEHICLE_CLASSES:
                count += 1
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return count, frame

# Open video streams
cap1 = cv2.VideoCapture(cam1_url)
cap2 = cv2.VideoCapture(cam2_url)

if not cap1.isOpened() or not cap2.isOpened():
    print("Error opening video streams")
    exit()

# State variables
last_switch = time.time()
green_lane = 1
current_mode = "NORMAL"  # <-- Fix: Initialize mode

# Main loop
while True:
    frame1 = get_frame(cap1)
    frame2 = get_frame(cap2)

    if frame1 is None or frame2 is None:
        print("Frame not received.")
        continue

    cars_lane1, frame1 = detect_vehicles(frame1)
    cars_lane2, frame2 = detect_vehicles(frame2)

    # Display car count
    cv2.putText(frame1, f"Cars: {cars_lane1}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame2, f"Cars: {cars_lane2}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show frames
    cv2.imshow("Lane 1", frame1)
    cv2.imshow("Lane 2", frame2)

    # Switching logic
    current_time = time.time()

    if current_time - last_switch >= 1:  # Check every second

        # If no vehicles in both lanes
        if cars_lane1 == 0 and cars_lane2 == 0:
            if current_mode != "NO":
                print("No vehicles detected → Blinking YELLOW")
                current_mode = "NO"

            # Continuously send "NO" every second to keep blinking
            if current_time - last_switch >= 1:
                esp.write(b"NO")
                print("Sent NO to ESP")
                last_switch = current_time
                time.sleep(0.1)  # Small delay to avoid overloading serial


            continue  # Skip rest of logic


        # Vehicles have returned → resume normal mode
        if current_mode == "NO":
            current_mode = "NORMAL"
            last_switch = current_time
            print("Vehicles detected again → Resuming normal signal cycle")

        # Switching between lanes based on time and vehicle count
        if green_lane == 1 and current_time - last_switch >= 5:
            next_duration = 8 if cars_lane2 >= 2 else 5
            green_lane = 2
            esp.write(f"L2_{next_duration}\n".encode())
            print(f"Switch → Lane 2 GREEN for {next_duration}s")
            last_switch = time.time()

        elif green_lane == 2 and current_time - last_switch >= 5:
            next_duration = 8 if cars_lane1 >= 2 else 5
            green_lane = 1
            esp.write(f"L1_{next_duration}\n".encode())
            print(f"Switch → Lane 1 GREEN for {next_duration}s")
            last_switch = time.time()

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap1.release()
cap2.release()
cv2.destroyAllWindows()
