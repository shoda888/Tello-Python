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


logger = logging.getLogger('TfPoseEstimatorRun')
logger.handlers.clear()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation run')
    parser.add_argument('--image', type=str, default='./images/p1.jpg')
    parser.add_argument('--model', type=str, default='cmu',
                        help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. '
                             'default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    args = parser.parse_args()

    w, h = model_wh(args.resize)
    if w == 0 or h == 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))

    # estimate human poses from a single image !
    image = common.read_imgfile(args.image, None, None)
    if image is None:
        logger.error('Image can not be read, path=%s' % args.image)
        sys.exit(-1)

    t = time.time()
    humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
    elapsed = time.time() - t

    ## file save 
    human_models = []
    for i,human in enumerate(humans):
        human_model = {}
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
            human_model[i] = [body_part.x, body_part.y,body_part.score]
        
        human_models.append(human_model)
    print('human_models')
    print(human_models)

    write_csv('uncho.csv',human_models[0])
    #############
    logger.info('inference image: %s in %.4f seconds.' % (args.image, elapsed))
    # plt.imshow(image)

    print(type(humans))
    print('---------------humans----------------')
    print(humans) # humansは画像内に存在している人数が要素数であるリスト形式、中に骨格モデルのデータが入っている
    image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

    cv2.imwrite("output_img.png",image)

    fig = plt.figure()
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.show()
    
    run_load_human_model.add_label()


    # try:

    #     fig = plt.figure()
    #     a = fig.add_subplot(2, 2, 1)
    #     a.set_title('Result')
    #     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #     cv2.imwrite("output_img.png",image)

    #     bgimg = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB)
    #     bgimg = cv2.resize(bgimg, (e.heatMat.shape[1], e.heatMat.shape[0]), interpolation=cv2.INTER_AREA)

    #     # show network output
    #     a = fig.add_subplot(2, 2, 2)
    #     plt.imshow(bgimg, alpha=0.5)
    #     tmp = np.amax(e.heatMat[:, :, :-1], axis=2)
    #     plt.imshow(tmp, cmap=plt.cm.gray, alpha=0.5)
    #     plt.colorbar()

    #     tmp2 = e.pafMat.transpose((2, 0, 1))
    #     tmp2_odd = np.amax(np.absolute(tmp2[::2, :, :]), axis=0)
    #     tmp2_even = np.amax(np.absolute(tmp2[1::2, :, :]), axis=0)

    #     a = fig.add_subplot(2, 2, 3)
    #     a.set_title('Vectormap-x')
    #     # plt.imshow(CocoPose.get_bgimg(inp, target_size=(vectmap.shape[1], vectmap.shape[0])), alpha=0.5)
    #     plt.imshow(tmp2_odd, cmap=plt.cm.gray, alpha=0.5)
    #     plt.colorbar()

    #     a = fig.add_subplot(2, 2, 4)
    #     a.set_title('Vectormap-y')
    #     # plt.imshow(CocoPose.get_bgimg(inp, target_size=(vectmap.shape[1], vectmap.shape[0])), alpha=0.5)
    #     plt.imshow(tmp2_even, cmap=plt.cm.gray, alpha=0.5)
    #     plt.colorbar()
    #     plt.show()
    # except Exception as e:
    #     logger.warning('matplitlib error, %s' % e)
    #     cv2.imshow('result', image)
    #     cv2.waitKey()
