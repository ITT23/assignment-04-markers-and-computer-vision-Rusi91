import cv2
import numpy as np
import pyglet
from PIL import Image
import sys
import cv2.aruco as aruco
from time import sleep

video_id = 0

hand_arr = []
corner_arr = []
center_marker = (0,0)

color = (255, 0, 0)

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

# how to get the webcam resolution: https://www.learnpythonwithrune.org/find-all-possible-webcam-resolutions-with-opencv-in-python/
WINDOW_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
WINDOW_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the ArUco dictionary and parameters
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

@window.event
def on_draw():
  global corner_arr, center_marker

  window.clear()
  ret, frame = cap.read()

  # Convert the frame to grayscale
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # Detect ArUco markers in the frame
  corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

  if len(corners) > 4:
    corner_arr = []

    for i in range(len(corners)):
      if ids[i][0] != 23:
        corner_arr.append([corners[i][0][0][0], corners[i][0][0][1]])
      else:
        x_sum = corners[i][0][0][0]+ corners[i][0][1][0]+ corners[i][0][2][0]+ corners[i][0][3][0]
        y_sum = corners[i][0][0][1]+ corners[i][0][1][1]+ corners[i][0][2][1]+ corners[i][0][3][1]
            
        x_centerPixel = x_sum*.25
        y_centerPixel = y_sum*.25

        center_marker = (int(x_centerPixel), int(y_centerPixel))

        print(center_marker)
    
  elif len(corners) >= 4 and 23 not in ids:
    corner_arr = []
    for i in range(len(corners)):
      corner_arr.append([corners[i][0][0][0], corners[i][0][0][1]])
    
    #print(corner_arr[0])
    #print(corner_arr[1])
    #print(corner_arr[2])
    #print(corner_arr[3])

  # Check if marker is detected
  if ids is not None:
      # Draw lines along the sides of the marker
      aruco.drawDetectedMarkers(frame, corners)

  if len(corners) >= 4:
    frame = get_transformed_img(frame, corner_arr[0], corner_arr[1], corner_arr[3], corner_arr[2])
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #frame = cv2.drawContours(frame, contours, -1, (255, 0, 0), 3)
    #frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #ret, thresh = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY)
    #contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #img_contours = cv2.drawContours(frame, contours, -1, (255,0,0), 3)
    
    #hand_arr = contours
    #print(hand_arr[0][0][0][0])

  if len(corners) >= 4:
    position = (300, 200)
    radius = (50)
    color = (255, 0, 0)
    border_width = -1 # -1 means that the shape is filled

    frame = cv2.circle(frame, position, radius, color, border_width)

    
      
    x_marker, y_marker = center_marker
    x_circle, y_circle = position

    print(x_marker)
    print(y_marker)

    if x_marker >= x_circle - radius and x_marker <= x_circle + radius and y_marker >= y_circle - radius and  y_marker <= y_circle + radius:
      print("JEtzt aber")
        

    

  img = cv2glet(frame, 'BGR')
  img.blit(0, 0, 0)

  sleep(0.1)
    

def get_transformed_img(img_param, marker_point_1, marker_point_2, marker_point_3, marker_point_4):
    img_copy_for_transformation = img_param.copy()

    img_width = img_param.shape[1]
    img_height = img_param.shape[0]

    input_points = np.float32(np.array([marker_point_1, marker_point_2, marker_point_3, marker_point_4]))
    destination = np.float32(np.array([[0, 0], [img_width, 0], [img_width, img_height], [0, img_height]]))
    matrix = cv2.getPerspectiveTransform(input_points, destination)
    img_transformed = cv2.warpPerspective(img_param, matrix, (img_width, img_height), flags=cv2.INTER_LINEAR)

    return img_transformed

pyglet.app.run()
