# Using the actual camera:
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[165,180]}  #Here is the range of H in the HSV color space represented by the color
kernel_5 = np.ones((5,5),np.uint8) #Define a 5×5 convolution kernel with element values of all 1.


def get_morphologyEx_img(img,color_name):

    # The blue range will be different under different lighting conditions and can be adjusted flexibly.  H: chroma, S: saturation v: lightness
    resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)  # In order to reduce the amount of calculation, the size of the picture is reduced to (160,120)
    hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # Convert from BGR to HSV
    color_type = color_name
    
    mask = cv2.inRange(hsv,np.array([min(color_dict[color_type]), 60, 60]), np.array([max(color_dict[color_type]), 255, 255]) )           # inRange()：Make the ones between lower/upper white, and the rest black
    if color_type == 'red':
            mask_2 = cv2.inRange(hsv, (color_dict['red_2'][0],0,0), (color_dict['red_2'][1],255,255)) 
            mask = cv2.bitwise_or(mask, mask_2)

    morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_5,iterations=1)              # Perform an open operation on the image 
    return morphologyEx_img

def morphologyEx_img_to_line_angle_and_x(morphologyEx_img, img, target_color='blue'):

    contours, hierarchy = cv2.findContours(morphologyEx_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large


    if len(contours) == 0:
        # No possible lines detected.
        return None
    
    line_scores = []
    line_angles = []
    line_xs = []
    for contour in contours:    # Traverse all contours
        x,y,w,h = cv2.boundingRect(contour)      # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

        # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
        if w >= 8 and h >= 8: # Because the picture is reduced to a quarter of the original size, if you want to draw a rectangle on the original picture to circle the target, you have to multiply x, y, w, h by 4.
            x = x * 4
            y = y * 4 
            w = w * 4
            h = h * 4
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)  # Draw a rectangular frame
            cv2.putText(img,target_color,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)# Add character description
        
        # score this possible line.
        line_scores.append(h * (1 - y)) # high scores for long lines that start near the bottom of the image.
        contour_points = contour.reshape(-1, 2) # reshape to rows of points
        x_at_top = contour_points[np.argmax(contour_points[:, 1])][0]
        x_at_bottom = contour_points[np.argmin(contour_points[:, 1])][0]
        angle = np.arctan2(x_at_top - x_at_bottom, h)
        line_angles.append(angle)
        line_xs.append(x + w/2) # Center of the bottom of the line

    chosen_line_index = np.argmax(line_scores)
    angle = line_angles[chosen_line_index]
    x = line_xs[chosen_line_index]
    # Correct to 0 in the middle of the image, turn into a ratio.
    x = (x - morphologyEx_img.shape[0] / 2) / (morphologyEx_img.shape[0] / 2)
    # x now ranges from [-1, 1] based on where it is in the image.
    return angle, x

def line_angle_and_x_to_heading_angle(angle, x):
    # Try to match angle, but correct if x is offcenter.
    x = -x # positive x is now to the left, to match the picar heading angle.
    correction = x * 10 * np.pi/180 # Adjust by up to 10 degrees towards x, the base of the line in view.
    return angle + correction


from maneuvers import go # basic move function, defined earlier
def follow_line_camera(picarx, target_color='blue'):

    #init camera
    print("start")
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=camera.resolution)  

    for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):# use_video_port=True
        img = frame.array
        morphologyEx_img = get_morphologyEx_img(img, target_color)
        angle, x = morphologyEx_img_to_line_angle_and_x(morphologyEx_img, img, target_color)
        heading_angle = line_angle_and_x_to_heading_angle(angle, x)

        go(picarx, angle=heading_angle, speed=40)

        cv2.imshow("video", img)    # OpenCV image show
        cv2.imshow("morphologyEx_img", morphologyEx_img)    # OpenCV image show
        rawCapture.truncate(0)   # Release cache
    
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            camera.close()
            break

