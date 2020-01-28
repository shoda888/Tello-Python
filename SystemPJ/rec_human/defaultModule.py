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
import os


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
    def __init__(self,drone):
        """
        Defaultクラスの初期化
        """
        # absl.flag関係の設定
        self.FLAGS = flags.FLAGS
        flags.DEFINE_string('classes', './rec_human/data/coco.names', 'path to classes file')
        flags.DEFINE_string('weights', './rec_human/checkpoints/yolov3.tf',
                            'path to weights file')
        flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
        flags.DEFINE_integer('size', 416, 'resize images to')
        flags.DEFINE_string('video', './rec_human/data/video.mp4',
                            'path to video file or number for webcam)')
        flags.DEFINE_string('output', None, 'path to output video')
        flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
        flags.DEFINE_integer('num_classes', 80, 'number of classes in the model')

        
        self.drone = drone # Telloインスタンスの設定
        self.pre_time = time.time()
        self.center = False


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
        center = False # 中央合わせ用のフラグ

        while True:
            self.drone.detect_flag = False # 中央合わせを行う関係上，ここで1度フラグを倒しておく
            
            # 変数の初期化
            bound = np.array([0, 0, 0, 0])
            area = 0

            frame = self.drone.read()    # 映像を1フレーム取得
            if frame is None or frame.size == 0:    # 中身がおかしかったら無視
                continue 

            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する
            frame = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更


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

            # 何か物体を検知した場合，人かどうかを判定する．人であれば画像処理を行い，矩形が中央にあるかの判定を行う
            if nums != 0:

                # 検出結果に対し，もっとも近い人のboundを抽出
                boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]
                wh = np.flip(img.shape[0:2])
                for i in range(nums):
                    x1,y1 = ((np.array(boxes[i][0:2]) * wh).astype(np.int32))
                    x2,y2 = ((np.array(boxes[i][2:4]) * wh).astype(np.int32))
                    area0 =(x2-x1)*(y2-y1) # 検出した矩形の面積を計算
                    if classes[i] == 0 and scores[i] > 0.95 and area0 > area: # 検出結果が"person"で，面積がもっとも大きければboundを更新
                        self.drone.detect_flag = True # detectフラグを立てる
                        area = area0 # 矩形の面積を保存
                        bound = np.array([x1, y1, x2-x1, y2-y1]) # boundを更新
                
                # 人を検出していた場合の処理
                if self.drone.detect_flag:
                    cnt = 0 # 探索用カウンタのクリア

                    # 検出結果の画像への書き込み
                    img = cv2.rectangle(img, (bound[0],bound[1]), (bound[0]+bound[2], bound[1]+bound[3]), (0, 0, 255), 2) # 抽出した人の領域を書き込み
                    img = cv2.putText(img, "person",
                    (bound[0],bound[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2) # "person"の書き込み，なくていいかも
                    img = cv2.putText(img, "Time: {:.2f}ms".format(sum(times)/len(times)*1000), (0, 30),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2) # 検出時間の書き込み
                    
                    # 検出した人の矩形を画面中央に合わせるための処理
                    x = bound[0] # 人の矩形の始点
                    w = bound[2] - bound[0] # 矩形の幅
                    cx = int( x + w/2 ) # 矩形の中央x座標

                    # 矩形のx座標中央が画像中央にあればcenterフラグを立てる
                    if abs(240 - cx) < 20.0: 
                        center = True
            
            # 処理を行なった取得画像の表示
            cv2.imshow("detect", img)
            cv2.waitKey(1)

            
            # 検出結果をもとに終了判定，そうでなければ移動を行う
            if center: # 人の矩形の中央合わせが終了していれば後処理を行い，ループを終了する
                print("centering")
                cv2.imwrite("detect.png", img) # 中央合わせ終了後の画像を保存，デバッグ用

                # Openposeの適用
                cv2.imwrite('./../openpose/images/input.jpg',image)
                os.system('python3 ./../openpose/play.py')
                break
            elif not center and self.drone.detect_flag: # 人を検知しており，中央合わせが済んでいなければP制御で中央合わせを行う
                d = 0   # rcコマンドの初期値は0

                # 目標位置との差分にゲインを掛ける（P制御)
                dx = 0.2 * (240 - cx)       # 画面中心との差分

                dx = -dx # 制御方向が逆だったので，-1を掛けて逆転させた

                # 旋回方向の不感帯を設定
                d = 0.0 if abs(dx) < 20.0 else dx   # ±20未満ならゼロにする
                # 旋回方向のソフトウェアリミッタ(±100を超えないように)
                d =  100 if d >  100.0 else d
                d = -100 if d < -100.0 else d

                print("dx:" + str(dx))

                # rcコマンドを送信
                self.drone.send_command('rc %s %s %s %s'%(0, 0, 0, int(d)) )                
            elif not self.drone.detect_flag: # 人を検出していなければ旋回を行う
                cnt += 1 # 探索用カウンタを増加
                self.drone.rotate_cw(45) # 45度旋回

                # その場で一回転していたら少し前進する
                if cnt == 8 :
                    self.drone.move_forward(1) # 1m前進
                    cnt = 0 # 探索用カウンタのクリア
            else: # 例外処理
                print("detectメソッド内での例外")
                self.drone.land() # 着陸
                sys.exit() # システムの終了


            # 5秒おきに'command'を送って、死活チェックを通す
            current_time = time.time()  # 現在時刻を取得
            if current_time - self.pre_time > 5.0 :  # 前回時刻から5秒以上経過しているか？
                self.drone.send_command('command')   # 'command'送信
                self.pre_time = current_time         # 前回時刻を更新

        return frame, bound

def main(_argv):
    # デバッグ用
    im = cv2.imread('/rec_human/test.jpg')
    default = Default()
    bound = default.detect(im)
    print(bound)


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass