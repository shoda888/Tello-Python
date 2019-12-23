import pickle
from tf_pose import common
import cv2

image_w = 1024
image_h = 1280
f = open("humans_model.txt","rb")
humans = pickle.load(f)
f.close()

for i,human in enumerate(humans):
    print(i,': times')
    print('x: ',human)
    
    # draw point
    for i in range(common.CocoPart.Background.value):
        
        if i not in human.body_parts.keys():
            continue

        body_part = human.body_parts[i]
        # for x in dir(body_part):   # body_part.scoreは各点における信頼度っぽい。
        #     print(x)
        print(i,'  ---  ',body_part)
        print(body_part.x)
        center = (int(body_part.x * image_w + 0.5), int(body_part.y * image_h + 0.5))
        