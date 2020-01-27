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
        """
        Defaultクラスの初期化
        """
        # absl.flag関係の設定
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

        
        # self.drone = drone # Telloインスタンスの設定


        # yoloインスタンスの設定
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

    def detect(self):
        """
        被災者をyoloを用いて発見，bboxを作成するメソッド

        Return:
            frame int:
                人を検知した時の画像
            bound int:
                検知した人の領域
        """

        self.drone.detect_flag = False # detectフラグの初期化
        cnt = 0 # 探索用のカウンタの初期化

        while True:
            frame = self.drone.read()    # 映像を1フレーム取得
            if frame is None or frame.size == 0:    # 中身がおかしかったら無視
                continue 

            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する
            frame = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更

            # 変数の初期化
            bound = np.array([0, 0, 0, 0])
            area = 0
            

            # yoloによる画像認識
            img = frame

            img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_in = tf.expand_dims(img_in, 0)
            img_in = transform_images(img_in, FLAGS.size)

            t1 = time.time()
            boxes, scores, classes, nums = self.yolo.predict(img_in) # 画像に対してyoloを適用
            t2 = time.time()
            self.times.append(t2-t1)
            times = self.times[-20:]

            if nums != 0: # 何か物体を検知した場合
                

                # 検出結果に対し，もっとも近い人のboundを抽出
                boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]
                wh = np.flip(img.shape[0:2])
                for i in range(nums):
                    x1,y1 = ((np.array(boxes[i][0:2]) * wh).astype(np.int32))
                    x2,y2 = ((np.array(boxes[i][2:4]) * wh).astype(np.int32))
                    area0 =(x2-x1)*(y2-y1) # 検出した矩形の面積を計算
                    if classes[i] == 0 and area0 > area: # 検出結果が"person"で，面積がもっとも大きければboundを更新
                        self.drone.detect_flag = True # detectフラグを立てる
                        area = area0 # 矩形の面積を保存
                        bound = np.array([x1, y1, x2, y2]) # boundを更新

                img = cv2.rectangle(img, (x1,y1), (x2,y2), (0, 0, 255), 2) # 抽出した人の領域を書き込み
                img = cv2.putText(img, '{} {:.4f}'.format(
                self.class_names[int(classes[0])], scores[0]),
                (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2) # "person"の書き込み，なくていいかも

                # 検出時間の書き込み
                img = cv2.putText(img, "Time: {:.2f}ms".format(sum(times)/len(times)*1000), (0, 30),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)

            # 検出結果の表示
            cv2.imshow('detection', img)
            cv2.waitKey(5)

            if self.drone.detect_flag: # detectフラグが立っていれば探索を終了する
                print("人を検知しました")
                break
            else: # フラグが立っていなければ旋回を行い，もう一度画像検知を行う
                cnt += 1 # 探索用カウンタを増加
                self.drone.rotate_cw(20) # 20度旋回

                if cnt == 18 : # その場で一回転していたら少し前進する
                    self.drone.move_forward(1) # 1m前進
                    cnt = 0 # 探索用カウンタのリセット

        return frame, bound

def main(_argv):
    # デバッグ用
    im = cv2.imread('test.jpg')
    default = Default()
    bound = default.detect(im)
    print(bound)


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass