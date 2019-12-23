import pickle
import cv2

image_w = 1024
image_h = 1280
f = open("humans_model.txt","rb")
humans = pickle.load(f)
f.close()

# class CocoPart(Enum):
#     Nose = 0
#     Neck = 1
#     RShoulder = 2
#     RElbow = 3
#     RWrist = 4
#     LShoulder = 5
#     LElbow = 6
#     LWrist = 7
#     RHip = 8
#     RKnee = 9
#     RAnkle = 10
#     LHip = 11
#     LKnee = 12
#     LAnkle = 13
#     REye = 14
#     LEye = 15
#     REar = 16
#     LEar = 17
#     Background = 18


common_values = 18

for i,human in enumerate(humans):
    print(i,': times')
    print('x: ',human)
    
    # draw point
    for i in range(common_values):
        
        if i not in human.body_parts.keys():
            continue

        body_part = human.body_parts[i]
        # for x in dir(body_part):   # body_part.scoreは各点における信頼度っぽい。
        #     print(x)
        print(i,'  ---  ',body_part)
        print(body_part.x)
        center = (int(body_part.x * image_w + 0.5), int(body_part.y * image_h + 0.5))
        