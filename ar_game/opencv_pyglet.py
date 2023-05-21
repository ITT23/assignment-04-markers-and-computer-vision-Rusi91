import cv2
import numpy as np
import pyglet
from PIL import Image
import sys
import cv2.aruco as aruco

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# converts OpenCV image to PIL image and then to pyglet texture
# https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img,fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Define the ArUco dictionary and parameters
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

@window.event
def on_draw():
    window.clear()
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers in the frame
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    if len(corners) == 4:
       print(corners[0][0][0][1])
       print(corners[0][0][1][1])
       print(corners[0][0][2][1])
       print(corners[0][0][3][1])

    # Check if marker is detected
    if ids is not None:
        # Draw lines along the sides of the marker
        aruco.drawDetectedMarkers(frame, corners)


    img = cv2glet(frame, 'BGR')
    img.blit(0, 0, 0)

pyglet.app.run()
