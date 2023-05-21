# AR GAME:
#   
#   REQUIREMENTS: 
#       you need a additional aruco marker. I uploaded the marker 'game_marker.jpg'. 
#       If you want to use another marker you just need to adjust GAME_MARKER_ID below.
#                    
#   HOW THE GAME WORKS:
#       in zoomed / transformed mode the user sees a circle
#       the user needs to use the 5th marker (gaming marker) to touch with it the circle
#       if the gaming marker (center position) touches the circle, the circle disappears and a new circle is drown at a random position and random color
# 
#   DISCLAIMER: 
#       I really tried to make a game where the user hand gets detected / tracked but i faild
#       I tried it with the countour detection but somehow had problems with the collision detection
#       My approach was to detect the collision with the circle through checking if the position coordinates of the circle are colliding with
#       one of the coordinates of the contour coordinates. At the end my hand was detected correctly (the contours surrounded only my hand) but
#       the problem was that the x-value of the the contour coordinates was always 0 - 5 while thy y-value was correct.
#       So as a result, i tried another gaming idea (which is described above)

import cv2
import numpy as np
import pyglet
from PIL import Image
import sys
import cv2.aruco as aruco
from time import sleep

video_id = 0

FPS = 10
DRAW_FREQUENCY = 1 / FPS
# id of the game marker.
# you can find it as 'game_marker.jpg'
# if you want to use another marker, change the id here
GAME_MARKER_ID = 23

# stores the corner points of the markers
corner_arr = []
# coordinates of the 5th marker (game marker)
center_marker = (0,0)
# achieved points
points = 0

# font of the displayed points text
FONT = cv2.FONT_HERSHEY_SIMPLEX
# fontScale of the displayed points text
FONT_SCALE = 1
# color of the displayed points text
COLOR = (0, 0, 255) # red
# Line thickness of the displayed points text
THICKNESS = 1 # 1 px

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

# displayed cirle for the AR game
circle_position = (300,200)
circle_color = (255, 0, 0)

@window.event
def on_draw():
  global corner_arr, center_marker, points, circle_position, circle_color

  window.clear()
  ret, frame = cap.read()

  # Convert the frame to grayscale
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # Detect ArUco markers in the frame
  corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

  if len(corners) > 4:
    corner_arr = []

    for i in range(len(corners)):
      # id 23 is the aruco marker for the game
      if ids[i][0] != GAME_MARKER_ID:
        # save the corner points
        corner_arr.append([corners[i][0][0][0], corners[i][0][0][1]])
      else:
        # get coordinates for the center of the aruco marker for the game
        # source how to get the center: https://stackoverflow.com/questions/53460495/finding-the-center-of-an-aruco-marker
        x_sum = corners[i][0][0][0]+ corners[i][0][1][0]+ corners[i][0][2][0]+ corners[i][0][3][0]
        y_sum = corners[i][0][0][1]+ corners[i][0][1][1]+ corners[i][0][2][1]+ corners[i][0][3][1]
            
        x_centerPixel = x_sum*.25
        y_centerPixel = y_sum*.25

        center_marker = (int(x_centerPixel), int(y_centerPixel))
  
  # without the game marker just save the corner points
  elif len(corners) >= 4 and GAME_MARKER_ID not in ids:
    corner_arr = []
    for i in range(len(corners)):
      corner_arr.append([corners[i][0][0][0], corners[i][0][0][1]])

  # Check if marker is detected
  if ids is not None:
      # Draw lines along the sides of the marker
      aruco.drawDetectedMarkers(frame, corners)

  # extract the region between the markers and transform it to a rectangle
  if len(corners) >= 4:
    frame = get_transformed_img(frame, corner_arr[0], corner_arr[1], corner_arr[3], corner_arr[2])

  if len(corners) >= 4:
    # draw circle for the game
    radius = (100)
    border_width = -1 # -1 means that the shape is filled
    frame = cv2.circle(frame, circle_position, radius, circle_color, border_width)
    # center of the game marker
    x_marker, y_marker = center_marker
    # center of the game circle
    x_circle, y_circle = circle_position
    
    # if center coordinates of the game marker collide with the circle -> destro circle, draw new circle and grand 1 point
    if x_marker >= x_circle - radius and x_marker <= x_circle + radius and y_marker >= y_circle - radius and  y_marker <= y_circle + radius:
      points += 1
      # draw new circle with random color (not white) and random position
      get_random_color()
      get_random_pos()
    # draw achieved points
    frame = cv2.putText(frame, "POINTS: " + str(points), (400, 50), FONT, FONT_SCALE, 
                    COLOR, THICKNESS, cv2.LINE_AA, False)
  # draw final image
  img = cv2glet(frame, 'BGR')
  img.blit(0, 0, 0)

  sleep(DRAW_FREQUENCY)
    
# get the transformed image
# It is code that we have been provided with from the last exercise. This code has been adjusted and expanded.
def get_transformed_img(img_param, marker_point_1, marker_point_2, marker_point_3, marker_point_4):

    img_width = img_param.shape[1]
    img_height = img_param.shape[0]

    input_points = np.float32(np.array([marker_point_1, marker_point_2, marker_point_3, marker_point_4]))
    destination = np.float32(np.array([[0, 0], [img_width, 0], [img_width, img_height], [0, img_height]]))
    matrix = cv2.getPerspectiveTransform(input_points, destination)
    img_transformed = cv2.warpPerspective(img_param, matrix, (img_width, img_height), flags=cv2.INTER_LINEAR)

    return img_transformed

# random color for every new circle
def get_random_color():
    global circle_color
    # avoid white because of white background
    r = np.random.randint(0,180)
    g = np.random.randint(0,180)
    b = np.random.randint(0,180)
    circle_color = (r,g,b)

# random position for every new circle
def get_random_pos():
    global circle_position
    x = np.random.randint(50, 400)
    y = np.random.randint(50, 300)
    circle_position = (x,y)

pyglet.app.run()
