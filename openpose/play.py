import run_function
import cv2
import os
import sys

sys.path.append('/Users/mineyukitakuma/Tello-Python/openpose/')
path = '/Users/mineyukitakuma/Tello-Python/openpose/images/input.jpg'
input_img = cv2.imread(path, cv2.IMREAD_COLOR)

run_function.openpose(image=input_img)
 

# path = './images/p1.jpg'
# input_img = cv2.imread(path, cv2.IMREAD_COLOR)

# run_function.openpose(image=input_img)


# path = './images/p1.jpg'
# input_img = cv2.imread(path, cv2.IMREAD_COLOR)

# run_function.openpose(image=input_img)
