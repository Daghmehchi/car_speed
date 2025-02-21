#================== Upload model and data ==================

!git clone https://github.com/Daghmehchi/Road-suitable-speed.git
!pip install -q -r /content/Road-suitable-speed/requirements.txt

import rarfile
import os

rar_path = "/content/Road-suitable-speed/models/best_sign/best_sign.part1.rar"
extract_path = "/content/Road-suitable-speed/models/best_sign"
with rarfile.RarFile(rar_path) as rf:
    rf.extractall(extract_path)

rar_path = "/content/Road-suitable-speed/models/best_weather/best_weather.part1.rar"
extract_path = "/content/Road-suitable-speed/models/best_weather"
with rarfile.RarFile(rar_path) as rf:
    rf.extractall(extract_path)

#================== Input video ==================
from google.colab import files
from IPython.display import HTML


def upload_video(default_path):
    print("لطفاً ویدئوی خود را آپلود کنید یا بر روی گذینه لغو کلیک کنید")
    uploaded = files.upload()

    if uploaded:
        video_path = list(uploaded.keys())[0]
    else:
        video_path = default_path  # if upload canceled take defult pass
    return video_path

default_video_path = "/content/Road-suitable-speed/test_objects/test_video_Trim.mkv"
video_path = upload_video(default_video_path)
# video_path is inpot video path

#================== Traffic signs detection ==================

road_speed = None
last_class = None
time = None

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import torch
import cv2
import sys

# Load the YOLOv5 model
model_path = '/content/Road-suitable-speed/models/best_sign/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
model.conf = 0.8  # Set confidence threshold

# Open the video file
cap = cv2.VideoCapture(video_path)

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
output_path = '/content/Road-suitable-speed/output/sign_proces_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Process each frame in the video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # Exit loop if no frame is returned (end of video)

    # Perform detection on the current frame
    results = model(frame)

    # Access results
    boxes = results.xyxy[0].tolist()  # Extract boxes and convert to list

    # Draw boxes on the frame
    for result in boxes:
        x1, y1, x2, y2, confidence, cls = result
        label = f'{int(cls)} {confidence:.2f}'
        last_class = int(cls)

        # Draw rectangle and label
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, label, (int(x1), int(y1) - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Write the frame with detections to output video
    out.write(frame)

cap.release()
out.release()

# names = ['Green Light', 'Red Light', 'Speed Limit 10', 'Speed Limit 100', 'Speed Limit 110', 'Speed Limit 120', 'Speed Limit 20', 'Speed Limit 30', 'Speed Limit 40', 'Speed Limit 50', 'Speed Limit 60', 'Speed Limit 70', 'Speed Limit 80', 'Speed Limit 90', 'Stop']
limits = [None, 0, 10, 100, 110, 120, 20, 30, 40, 50, 60, 70, 80, 90, 0]

if 0 < last_class < len(limits):
    road_speed = limits[last_class]

print(f"Road speed ​​in interaction with traffic signs is: {road_speed}")

#================== Day or Night ==================

from datetime import datetime

# geting system time
now = datetime.now()

current_hour = now.hour

# loop for determining day and night
# 0 = day   1 = night
if 6 <= current_hour < 18:
    road_speed = road_speed
    timeL = 'Day'
else:
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction
    timeL = 'Night'
print(f"Road speed ​​in interaction with time is: {road_speed}")

#================== Weather detection ==================

cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()  # read first frame
if ret:
    cv2.imwrite('/content/Road-suitable-speed/output/frame1.jpg', frame)  #save first frame as image

cap.release()

from ultralytics import YOLO

# Load a model
model = YOLO("/content/Road-suitable-speed/models/best_weather/best_weather.pt")  # load a custom model

# Predict with the model
results = model("/content/Road-suitable-speed/output/frame1.jpg")  # predict on an image


annotated_image = results[0].plot()  # save image with results
output_image_path = '/content/Road-suitable-speed/output/weather_image.jpg'
cv2.imwrite(output_image_path, annotated_image)

# Get top5 class indices and their confidence scores
top5_indices = results[0].probs.top5
top5_confidences = results[0].probs.top5conf

# Filter and print classes with confidence greater than 60%
filtered_classes = [(model.names[index], confidence)for index, confidence in zip(top5_indices, top5_confidences) if confidence > 0.6]
#print(filtered_classes)  # empety if < 0.6

# weather = ['fog','hail','ice','rain','sandstorm','snow','sun','clear','cloud']

if filtered_classes == [] :
    road_speed = road_speed

elif filtered_classes[0][0] == 'clear' or 'cloud' :
    road_speed = road_speed

elif filtered_classes[0][0] == 'fog' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'hail' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'ice' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'rain' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'sandstorm' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'snow' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

elif filtered_classes[0][0] == 'sun' :
    reduction = road_speed * 0.15
    road_speed = road_speed - reduction

print(f"Road speed ​​in interaction with weather is: {road_speed}")

#================== vehicle in front speed detection ==================

c_speed = road_speed
average_speed = None


import numpy as np

cap = cv2.VideoCapture(video_path) # read video

width = int(cap.get(3))
height = int(cap.get(4))
top_width = width // 6
bottom_width = width
top_height = int(height * 0.3)

top_left = ((width - top_width) // 2, 260)
top_rigth = ((width + top_width) // 2, 410)
bottom_left = (0, height - 80)
bottom_right = (width, height - 80)

#filterin of video
vertices = np.array([[top_left, top_rigth, bottom_right, bottom_left]], dtype = np.int32)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('/content/Road-suitable-speed/output/crop_video.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (width, height))

while cap.isOpened(): # open video frame by frame
    ret, frame = cap.read()
    if not ret:
        break

    mask = np.zeros_like(frame)
    cv2.fillPoly(mask, vertices, (255, 255, 255))

    filtered_frame = cv2.bitwise_and(frame, mask)
    out.write(filtered_frame)

cap.release()
out.release()

from time import time
from ultralytics import YOLO

video_path_c = '/content/Road-suitable-speed/output/crop_video.mp4'
model_path = YOLO('yolov8m.pt')

model = model_path  

# car detection function not plate is just name
def detect_license_plate(frame):
    results = model.predict(source=frame, save=False, verbose=False)
    boxes = results[0].boxes

    if boxes:
        confidences = boxes.conf.cpu().numpy()
        max_conf_idx = confidences.argmax()

        # best box information
        best_box = boxes[max_conf_idx]
        x1, y1, x2, y2 = map(int, best_box.xyxy[0])
        confidence = best_box.conf.item()

        if confidence >= 0.6:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Conf: {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame, boxes

cap = cv2.VideoCapture(video_path_c)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_path = '/content/Road-suitable-speed/output/speed_video.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

prev_time = time()
prev_position = None
speed_list = []

def adjust_speed(c_speed):    # apply realativ speed to car speed
    c_speed += average_speed
    if c_speed > road_speed:
        c_speed = road_speed
    return c_speed

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame, boxes = detect_license_plate(frame)

    if boxes is not None and len(boxes) > 0:
        confidences = [box.conf.item() for box in boxes]
        max_conf_idx = np.argmax(confidences)
        best_box = boxes[max_conf_idx]

        curr_position = (best_box.xyxy[0][0].item(), best_box.xyxy[0][1].item())
        if prev_position:
            # convert pixel change to meter
            distance = curr_position[0] - prev_position[0]
            speed = (distance * 3.6) / (time() - prev_time)
            speed_list.append(speed)

            # listing last 5 frame speed
            speed_list.append(speed)
            if len(speed_list) > 5:
              speed_list.pop(0)  

            # avrage 5 frame's speed
            average_speed = sum(speed_list) / len(speed_list)


        else:
            speed = 0
            average_speed = 0

        prev_position = curr_position
        prev_time = time()

        # show avrage and curent speed
        cv2.putText(frame, f'Current Speed: {speed:.2f} km/h', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f'Average Speed: {average_speed:.2f} km/h', (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        #average_speed can be print for every frame

        #print(adjust_speed(c_speed))
        #print speed in video
        center_coordinates, radius, thickness, color = (150, 200), 50, 8, (0, 0, 255) #circle information
        cv2.circle(frame, center_coordinates, radius, color, thickness)
        text = str(int(adjust_speed(c_speed)))
        font = cv2.FONT_HERSHEY_SIMPLEX  
        font_scale = 2  
        text_color = (255, 255, 255)  
        text_thickness = 5
        text_size = cv2.getTextSize(text, font, font_scale, text_thickness)[0]
        text_x = center_coordinates[0] - text_size[0] // 2
        text_y = center_coordinates[1] + text_size[1] // 2
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, text_thickness)

        text_1 = f"Weather , Time , Trafic sign: {filtered_classes[0][0]} , {timeL} , {road_speed}km/h"
        cv2.putText(frame, text_1 , (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    out.write(frame)

cap.release()
out.release()
