# -*- coding: utf-8 -*-

import time
from absl import app, flags, logging
from absl.flags import FLAGS
import numpy as np
import cv2
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs


"""
ドローンが人を認識していない時に，人を探すクラスを入れたモジュール
"""

class Default:
    """
    人を探索，検知するクラス

    Attributes:
        drone obj:
            操作するドローン
    """
    def __init__(self):
        self.FLAGS = flags.FLAGS
        flags.DEFINE_string('classes', './data/coco.names', 'path to classes file')
        flags.DEFINE_string('weights', './checkpoints/yolov3.tf',
                            'path to weights file')
        flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
        flags.DEFINE_integer('size', 416, 'resize images to')
        flags.DEFINE_string('video', './data/video.mp4',
                            'path to video file or number for webcam)')
        flags.DEFINE_string('output', None, 'path to output video')
        flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
        flags.DEFINE_integer('num_classes', 80, 'number of classes in the model')

        """
        Defaultクラスの初期化
        """
        # self.drone = drone

        physical_devices = tf.config.experimental.list_physical_devices('GPU')

        if len(physical_devices) > 0:
            tf.config.experimental.set_memory_growth(physical_devices[0], True)


        #self.yolo = YoloV3Tiny(classes=FLAGS.num_classes)
        self.yolo = YoloV3(classes=self.FLAGS.num_classes)

        self.yolo.load_weights(FLAGS.weights)
        print('weights loaded')

        self.class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
        print('classes loaded')

        self.times = []

    def detect(self, frame):
        """
        被災者をyoloを用いて発見，bboxを作成するメソッド
        """
        bound = None
        area = 0

        """
        Parameters:
            frame int:
                カメラ画像
        """

        """
        Return:
            bbox int:
                検知した人の領域
        """

        img = frame


        img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_in = tf.expand_dims(img_in, 0)
        img_in = transform_images(img_in, FLAGS.size)

        t1 = time.time()
        boxes, scores, classes, nums = self.yolo.predict(img_in)
        t2 = time.time()
        self.times.append(t2-t1)
        times = self.times[-20:]

        if nums != 0:
            # self.drone.detect_flag = True
            img = draw_outputs(img, (boxes, scores, classes, nums), self.class_names)

            img = cv2.putText(img, "Time: {:.2f}ms".format(sum(times)/len(times)*1000), (0, 30),
                          cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)

            cv2.imshow('detection', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]
            wh = np.flip(img.shape[0:2])
            for i in range(nums):
                x1,y1 = ((np.array(boxes[i][0:2]) * wh).astype(np.int32))
                x2,y2 = ((np.array(boxes[i][2:4]) * wh).astype(np.int32))
                area0 =(x2-x1)*(y2-y1)
                if area0 > area:
                    area = area0
                    bound = (x1,y1,x2,y2)

        return bound

def main(_argv):
    # デバッグ用
    im = cv2.imread('test.jpg')
    default = Default()
    default.detect(im)


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass