import run_function
import cv2

path = './images/iwasaki6.jpg'
input_img = cv2.imread(path, cv2.IMREAD_COLOR)

run_function.openpose(image=input_img)
 

# path = './images/p1.jpg'
# input_img = cv2.imread(path, cv2.IMREAD_COLOR)

# run_function.openpose(image=input_img)


# path = './images/p1.jpg'
# input_img = cv2.imread(path, cv2.IMREAD_COLOR)

# run_function.openpose(image=input_img)
