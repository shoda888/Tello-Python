# -*- coding: utf-8 -*-
import cv2
from detect_video import img, width, height
from tello import Tello
import time
#from main.py import x, y, w, h
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
"""
    def __init__(self, drone, frame, bbox, track_type):
        """
        Approachクラスの初期化
        """
        self.drone = drone # 操作するドローン
        self.tracker = self.select_tracker(track_type) # 指定されたタイプのトラッカーインスタンスの作成
        self.tracker.init(frame, bbox) # 作成したトラッカーの初期化．画像と認識した人の領域を与える

    def select_tracker(self, track_type):
        choice = input("Please select your tracker number: ")

        if choice == '0':
            tracker = cv2.TrackerBoosting_create()
        if choice == '1':
            tracker = cv2.TrackerMIL_create()
        if choice == '2':
            tracker = cv2.TrackerKCF_create()
        if choice == '3':
            tracker = cv2.TrackerTLD_create()
        if choice == '4':
            tracker = cv2.TrackerMedianFlow_create()

        """
        コンストラクタで用いるトラッカー初期化用のメソッド

        Args:
            track_type str:
                指定されたタイプのトラッカー

        Returns:
            tracker obj:
               指定されたタイプのトラッカーインスタンス
        """
        #tracker = cv2.TrackerBoosting_create() # テスト用に入れた

        return tracker


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

        success, roi = self.tracker.update(frame)
        (x,y,w,h) = tuple(map(int,roi))
        self.drone.approach_flag　== 0#見つけてないため
        if sucess:#追跡状態
            self.drone.approach_flag　== 1

        """
        searchメソッドで得たbboxを元に，cv2のトラッキングを用いながら
        被災者に接近するメソッド
        追跡できているとき
        制御部分の管理
        """
        #bboxの中心を判定　4辺の位置を平均化
        #頂点の位置(22,134)(257,44)...から作られる長方形
        #bbox_length 縦横
        """ 試しに自作したとこ　追跡少々改良

        bcent = (int(0.5*(bbox[0]+bbox[2])),int(0.5*(bbox[1]+bbox[3])))
        fcent = (240,180)#画像の中心点 ここは詳しく書き込み必須

        a = bf = ud = tu = 0
        #追跡部分
        #距離判定は人のbox比/全体サイズで行う
        #カクカク位置変更からゆっくり移動に変更

        bfa = (detect_video.width)*(detect_video.height)/(172800)
        if bfa < 0.1:#人との距離を保つ bbox小さくなりすぎた時
            bf = int(10 + 1/(bfa+0.01))
        elif bfa > 0.6:#これらの設定は不感帯も兼ねる
            bf = -1*int(10 + 1/(-1*bfa+1.01))
        else:
            bf = 0
            #drone.move_stop#ホバリングのまま

        tua = bcent(1,1)-fcent(1,1)
        if tua > 80:#見つけた人が中央から外れたら中央に移動する操作
            tu = 20+int(tua/4)
        elif tua < -80:#優先度は上から順に?
            tu = -20-int(tua/4)
        else:
            tu = 0

        uda = bcent(2,2)-fcent(2,2)
        if uda > 40:
            ud = 10+int(ud/4)
        elif uda < -40:
            ud = -10-int(ud/4)
        else:
            ud = 0

        drone.send_command('rc %s %s %s %s'%(int(a), int(bf), int(ud), int(tu)) )
            #速度データ送信

            以下CV-FACEのmainよりコピペ"""

            cx = int( x + w/2 )
            cy = int( y + h/2 )

            a = b = c = d = 0   # rcコマンドの初期値は0

            # 目標位置との差分にゲインを掛ける（P制御)
            dx = 0.4 * (240 - cx)       # 画面中心との差分
            dy = 0.4 * (180 - cy)       # 画面中心との差分
            dw = 0.8 * (100 - w)        # 基準顔サイズ100pxとの差分

            dx = -dx # 制御方向が逆だったので，-1を掛けて逆転させた

            print('dx=%f  dy=%f  dw=%f'%(dx, dy, dw) )  # printして制御量を確認できるように

            # 旋回方向の不感帯を設定
            d = 0.0 if abs(dx) < 20.0 else dx   # ±20未満ならゼロにする
            # 旋回方向のソフトウェアリミッタ(±100を超えないように)
            d =  100 if d >  100.0 else d
            d = -100 if d < -100.0 else d

            # 前後方向の不感帯を設定
            b = 0.0 if abs(dw) < 10.0 else dw   # ±10未満ならゼロにする
            # 前後方向のソフトウェアリミッタ
            b =  100 if b >  100.0 else b
            b = -100 if b < -100.0 else b


            # 上下方向の不感帯を設定
            c = 0.0 if abs(dy) < 30.0 else dy   # ±30未満ならゼロにする
            # 上下方向のソフトウェアリミッタ
            c =  100 if c >  100.0 else c
            c = -100 if c < -100.0 else c

            # rcコマンドを送信
            #drone.send_command('rc %s %s %s %s'%(int(a), int(b), int(c), int(d)) )


        else:
            self.drone.detect_flag　== 0#見つけたから
            print("追跡失敗でした…。")
        #detect側に移動する
        # 追跡が失敗した場合にdrone.detect_flagを倒す
        # 追跡が成功し，接近できた場合にはdrone.close_flagを立てる
