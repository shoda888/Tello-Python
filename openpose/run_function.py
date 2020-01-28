import argparse
import logging
import sys
import time

from tf_pose import common
import cv2
import numpy as np
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import matplotlib.pyplot as plt
import pickle
import csv

import run_load_human_model


def write_csv(file, save_dict):
    save_row = {}

    with open(file,'w') as f:
        writer = csv.DictWriter(f, fieldnames=save_dict.keys(),delimiter=",",quotechar='"')
        writer.writeheader()

        k1 = list(save_dict.keys())[0]
        length = len(save_dict[k1])

        for i in range(length):
            for k, vs in save_dict.items():
                save_row[k] = vs[i]

            writer.writerow(save_row)

def openpose(image,model='cmu',resize='0x0',resize_out_ratio=4.0):
    w, h = model_wh(resize)
    if w == 0 or h == 0:
        e = TfPoseEstimator(get_graph_path(model), target_size=(432, 368))
    else:
        e = TfPoseEstimator(get_graph_path(model), target_size=(w, h))

    # estimate human poses from a single image !
    if image is None:
        logger.error('Image can not be read, path=%s' %  image)
        sys.exit(-1)

    t = time.time()
    humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size= resize_out_ratio)
    elapsed = time.time() - t

    ## file save 
    human_models = []
    for i,human in enumerate(humans):
        human_model = {}      
        # draw point
        for i in range(common.CocoPart.Background.value):
            
            if i not in human.body_parts.keys():
                continue

            body_part = human.body_parts[i]
            human_model[i] = [body_part.x, body_part.y,body_part.score]
        
        human_models.append(human_model)
    print('human_models')
    print(human_models)

    # write_csv('uncho.csv',human_models[0])

    print(type(humans))
    print('---------------humans----------------')
    print(humans) # humans have some elements that is equal how many human
    image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

    cv2.imwrite("output_img.png",image)    
    # run_load_human_model.add_label()
