import cv2
import numpy as np
import command_line_text
from os import path

# original image
img = None
# copy of original image to work with
img_work_copy = None

# title of window
WINDOW_NAME = 'Preview Window'
# input points have also a text displayed. This constant defines the distance of the text (x-axis) from the marked point
INPUT_POINT_TEXT_DISTANCE = 10

# is true after images is loaded
# starts the extraction application window
extraction_state = False

# the 4 input points are stored here
input_points_arr = []
# input point text which is displayed near the input point
input_points_text_arr = ['[1] upper left corner', '[2] upper right corner', '[3] lower left corner', '[4] lower right corner']
# font of the displayed input point text
font = cv2.FONT_HERSHEY_SIMPLEX
# fontScale of the displayed input point text
fontScale = 0.5
# color of the displayed input point text
color = (0, 0, 255) # red
# Line thickness of the displayed input point text
thickness = 1 # 1 px

# get the transformed image
# It is code that we have been provided with from the last exercise. This code has been adjusted and expanded.
def get_transformed_img():
    # Since text is also used, another copy is made here so that it doesn't carry over into the transformed version.
    img_copy_for_transformation = img.copy()

    img_width = img_copy_for_transformation.shape[1]
    img_height = img_copy_for_transformation.shape[0]

    input_points = np.float32(np.array([input_points_arr[0], input_points_arr[1], input_points_arr[3], input_points_arr[2]]))
    destination = np.float32(np.array([[0, 0], [img_width, 0], [img_width, img_height], [0, img_height]]))
    matrix = cv2.getPerspectiveTransform(input_points, destination)
    img_transformed = cv2.warpPerspective(img_copy_for_transformation, matrix, (img_width, img_height), flags=cv2.INTER_LINEAR)

    return img_transformed

# handles mouse input 
def mouse_callback(event, x, y, flags, param):
    global img_work_copy, input_points_arr

    # if all 4 input points are not provided
    if len(input_points_arr) < 4:
         if event == cv2.EVENT_LBUTTONDOWN:
            # input point circle
            img_work_copy = cv2.circle(img_work_copy, (x, y), 5, (255, 0, 0), -1)
            # input point text
                # how to input text in cv2: https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/
            img_work_copy = cv2.putText(img_work_copy, input_points_text_arr[len(input_points_arr)], (x + INPUT_POINT_TEXT_DISTANCE, y), font, fontScale, 
                    color, thickness, cv2.LINE_AA, False)
            # save new input point
            input_points_arr.append([x,y])
    # if all 4 input points are provided
    else:
        # get transformed image
        img_work_copy = get_transformed_img()
        # set window title to 'Result View'
        cv2.setWindowTitle(WINDOW_NAME, "Result View")
            
    cv2.imshow(WINDOW_NAME, img_work_copy)

# handles key input
def key_callback(key):
    global img_work_copy, input_points_arr, extraction_state

    # escape key (googled the ord for esc -> 27)
    # discard the changes and start over
    if key == 27:
        img_work_copy = img.copy()
        input_points_arr = []
    # key s 
    # if all 4 input points are provided save the image
    elif key == ord('s'):
        if len(input_points_arr) >= 4:
            # ask for desired resolution (e.g. 600x600, 800x600, ...)
                # resolution query information
            print(command_line_text.RESOLUTION_QUERY_REQUIREMENT_INFO)
                # ask for resolution value before the x.
            print(command_line_text.RESOLUTION_QUERY_REQUIREMENT_PART_ONE)
            resolution_query_value_before_x = get_resolution_value()
                # ask for resolution value after the x. 
            print(command_line_text.RESOLUTION_QUERY_REQUIREMENT_PART_TWO)
            resolution_query_value_after_x = get_resolution_value()
                # resize the image to the input resolution
                # how to change the resolution: https://stackoverflow.com/questions/12988151/python-cv2-change-dimension-and-quality
            img_work_copy = cv2.resize(img_work_copy, (resolution_query_value_before_x, resolution_query_value_after_x))
            # ask for the output file path
            print(command_line_text.OUTPUT_FILE_PATH_QUERY)
            output_file_query = input(command_line_text.INPUT_TEXT)
            # to avoid bugs regarding the backslash, the input path gets converted into a raw string
            # how to convert a string to a raw string: https://java2blog.com/convert-string-to-raw-string-python/
            raw_output_file_path = output_file_query.encode('unicode_escape').decode()
            # save file
            cv2.imwrite(raw_output_file_path, img_work_copy)
            # notify user
            print("file was saved at: " + raw_output_file_path)
    # key n
    # restart with new image
    elif key == ord('n'):
        #cv2.destroyAllWindows()
        extraction_state = False

# ask for the resolution value (before/after the x) 
# if input not an integer -> ask again 
def get_resolution_value():
    try:
        resolution_value = int(input(command_line_text.INPUT_TEXT))
        return resolution_value
    except:
        print(command_line_text.INPUT_RESOLUTION_ERROR)
        get_resolution_value()
        
while True:
    # if image is not loaded yet
    if not extraction_state:
        # introduction
        print(command_line_text.INTRODUTION)
        # ask for image file path
        print(command_line_text.INPUT_FILE_PATH_QUERY)
        input_file_query = input(command_line_text.INPUT_TEXT)
        # if file path doesn't exist -> ask again
        if not path.isfile(input_file_query):
            while not path.isfile(input_file_query):
                print(command_line_text.INPUT_PATH_ERROR)
                input_file_query = input(command_line_text.INPUT_TEXT)
        # to avoid bugs regarding the backslash, the input path gets converted into a raw string
        # how to convert a string to a raw string: https://java2blog.com/convert-string-to-raw-string-python/
        raw_input_file_path = input_file_query.encode('unicode_escape').decode()
        img = cv2.imread(raw_input_file_path)
        # make a copy of the original image to work with
        img_work_copy = img.copy()
        # reset input points array -> this is need if user restarts with a new image
        input_points_arr = []
        # information about the extraction process
        print(command_line_text.EXTRACTION_INFO)
        # start extraction process
        extraction_state = True
        cv2.namedWindow(WINDOW_NAME)

    # if image is loaded    
    else:
        # handles mouse input
        cv2.setMouseCallback(WINDOW_NAME, mouse_callback)
        cv2.imshow(WINDOW_NAME, img_work_copy)
        key = cv2.waitKey(0)
        # handles key input
        key_callback(key)
