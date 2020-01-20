# -*- coding: utf-8 -*-
import cv2
from detect_video import img, width, height
from tello import Tello
import time
import matplotlib.pyplot as plt
#import cv2 mainであるから必要なし?

"""
ドローンが認識した人に対して追跡するクラスを入れたモジュール
"""

class Approach:
    """
        追跡機能を持つクラス

        Attributes:
            drone obj:
                操作するドローン
            frame int:
                カメラ画像
            bbox int:
                認識した人のバウンディングボックスの情報
            track_type str:
                トラッカーのタイプ
                    ・Boosting
                    ・MIL
                    ・KCF
                    ・TLD
                    ・MedianFlow　これが最適?
                の4種類から選択(詳細はググれ)
    """
    #drone = Tello('', 8889, command_timeout=.01)
    #操作するドローン
    #画像とbbox追加
    Args:
        frame int:
        ret, frame = cap.read()
        #カメラ画像
        #tracker
    tracker = cv2.TrackerMedianFlow_create()
    #cv::Ptr<cv::Tracker> trackerMEDIANFLOW = cv::Tracker::create("MEDIANFLOW");
    cv::Rect2d roiMEDIANFLOW = roi

    #cv2.bbox()

    def __init__(self, drone, frame, bbox, track_type):
        """
        Approachクラスの初期化
        """
        self.drone = drone # 操作するドローン
        self.tracker = self.select_tracker(track_type) # 指定されたタイプのトラッカーインスタンスの作成
        self.tracker.init(frame, bbox) # 作成したトラッカーの初期化．画像と認識した人の領域を与える

    def select_tracker(self, track_type):
        """
        コンストラクタで用いるトラッカー初期化用のメソッド
        """
        Args:
            track_type str:
                指定されたタイプのトラッカー

        Returns:
            tracker obj:
                指定されたタイプのトラッカーインスタンス
        """
        tracker = cv2.TrackerBoosting_create() # テスト用に入れた

        return tracker
        """

    def approach(self, frame):
        """
        認識した人をトラッカーを用いて追跡するメソッド
        いれた画像の
        """

        """
        #detectflag
        # 追跡が失敗した場合にdrone.detect_flagを倒す
        # 追跡が成功し，接近できた場合にはdrone.close_flagを立てる
        """

        success, roi = tracker.update(frame)
        (x,y,w,h) = tuple(map(int,roi))
        if sucess:
        """
        searchメソッドで得たbboxを元に，cv2のトラッキングを用いながら
        被災者に接近するメソッド
        追跡できているとき
        """
        #bboxの中心を判定　4辺の位置を平均化
        #頂点の位置(22,134)(257,44)...から作られる長方形
        #bbox_length 縦横
            bcent = (0.5*(bbox[0]+bbox[2]),(0.5*(bbox[1]+bbox[3])))
            fcent = (240,180)#画像の中心点 ここは詳しく書き込み必須

            #追跡部分
            #距離判定は人のbox比/全体サイズで行う
            if (detect_video.width)*(detect_video.height)/(172800) < 0.1:#人との距離を保つ bbox小さくなりすぎた時
                drone.move_forward(0.2)
            elif (detect_video.width)*(detect_video.height)/(172800) > 0.6:
                drone.move_backward(0.2)
            else:
                drone.move_stop#ホバリングのまま

            if (bcent(1,1)-fcent(1,1)) > 80:#見つけた人が中央から外れたら中央に移動する操作
                drone.move_left(0.05)
                drone.rotate_ccw(5)
            elif (bcent(1,1)-fcent(1,1)) < -80:#優先度は上から順に?
                drone.move_right(0.05)
                drone.rotate_cw(5)
            elif (bcent(2,2)-fcent(2,2)) > 40:
                drone.move_up(0.05)
            elif (bcent(2,2)-fcent(2,2)) < -40:
                drone.move_down(0.05)
            else:
                drone.move_stop#ホバリングのまま　このプログラムは対話時も維持

        else:
            drone.to_detect()
        #detect側に移動する
        # 追跡が失敗した場合にdrone.detect_flagを倒す
        # 追跡が成功し，接近できた場合にはdrone.close_flagを立てる
        return tracker
