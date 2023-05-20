import cv2
import numpy as np

img = cv2.imread('image_extraction\sample_image.jpg')
img_copy = img.copy()
WINDOW_NAME = 'Preview Window'

WIDTH = 800
HEIGHT = 800

crop_points = []

cv2.namedWindow(WINDOW_NAME)


# text
text = 'upper left corner'
  
# font
font = cv2.FONT_HERSHEY_SIMPLEX
  
# fontScale
fontScale = 0.5
   
# Red color in BGR
color = (0, 0, 255)
  
# Line thickness of 2 px
thickness = 1

def get_transformed_img():

    img_copy_copy = img.copy()

    points = np.float32(np.array([crop_points[0], crop_points[1], crop_points[3], crop_points[2]]))

    destination = np.float32(np.array([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]]))

    matrix = cv2.getPerspectiveTransform(points, destination)

    img_transformed = cv2.warpPerspective(img_copy_copy, matrix, (WIDTH, HEIGHT), flags=cv2.INTER_LINEAR)

    return img_transformed

def mouse_callback(event, x, y, flags, param):
    global img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        img_copy = cv2.circle(img_copy, (x, y), 5, (255, 0, 0), -1)


        img_copy = cv2.putText(img_copy, text, (x,y), font, fontScale, 
                 color, thickness, cv2.LINE_AA, False)



        
        crop_points.append([x,y])
        print((x,y))

        if len(crop_points) > 4:
            print("jetzt")
            img_copy = get_transformed_img()

        cv2.imshow(WINDOW_NAME, img_copy)



while True:
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    
    cv2.imshow(WINDOW_NAME, img_copy)
    

    cv2.waitKey(0)
