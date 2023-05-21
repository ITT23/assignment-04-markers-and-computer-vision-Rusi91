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
      corner_1 = [corners[0][0][0][0], corners[0][0][0][1]]
      corner_2 = [corners[1][0][0][0], corners[1][0][0][1]]
      corner_3 = [corners[2][0][0][0], corners[2][0][0][1]]
      corner_4 = [corners[3][0][0][0], corners[3][0][0][1]]

      print(corner_1)
      print(corner_2)
      print(corner_3)
      print(corner_4)

    # Check if marker is detected
    if ids is not None:
        # Draw lines along the sides of the marker
        aruco.drawDetectedMarkers(frame, corners)

    if len(corners) == 4:
      frame = get_transformed_img(frame, corner_2, corner_1, corner_3, corner_4)


    img = cv2glet(frame, 'BGR')
    img.blit(0, 0, 0)

def get_transformed_img(img_param, point_one, point_two, point_three, point_four):
    img_copy_for_transformation = img_param.copy()

    img_width = img_copy_for_transformation.shape[1]
    img_height = img_copy_for_transformation.shape[0]

    input_points = np.float32(np.array([point_one, point_two, point_three, point_four]))
    destination = np.float32(np.array([[0, 0], [img_width, 0], [img_width, img_height], [0, img_height]]))
    matrix = cv2.getPerspectiveTransform(input_points, destination)
    img_transformed = cv2.warpPerspective(img_copy_for_transformation, matrix, (img_width, img_height), flags=cv2.INTER_LINEAR)

    return img_transformed

pyglet.app.run()
