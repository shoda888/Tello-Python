# -*- coding: utf-8 -*-
import cv2
import time
import numpy as np

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
    def __init__(self, drone, frame, bbox):
        """
        Approachクラスの初期化
        """
        self.drone = drone # 操作するドローン
        self.tracker = self.select_tracker() # 指定されたタイプのトラッカーインスタンスの作成
        self.tracker.init(frame, bbox) # 作成したトラッカーの初期化．画像と認識した人の領域を与える

    def select_tracker(self):
        """
        コンストラクタで用いるトラッカー初期化用のメソッド

        Returns:
            tracker obj:
               指定されたタイプのトラッカーインスタンス
        """
        print("0:Boosting")
        print("1:MIL")
        print("2:KCF")
        print("3:TLD")
        print("4:MedianFlow")
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

        return tracker


    def approach(self):
        """
        認識した人をトラッカーを用いて追跡するメソッド
        """

        self.drone.approach_flag = False # approachフラグの初期化

        while True:
            frame = self.drone.read()    # 映像を1フレーム取得
            if frame is None or frame.size == 0:    # 中身がおかしかったら無視
                continue 

            # (B)ここから画像処理
            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する
            frame = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更

            success, roi = self.tracker.update(frame) # トラッカーのアップデート
            

            # ドローンの制御部．Tello-CV-faceのコピペなので要調整
            if sucess: # 追跡状態
                (x,y,w,h) = tuple(map(int,roi)) # bboxの情報を取得
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
                drone.send_command('rc %s %s %s %s'%(int(a), int(b), int(c), int(d)) )

                # 検出した顔に枠を書く
                for (x, y, w, h) in pre_faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # 検出結果を書き込んだ画像を表示
                cv2.imshow("Approaching", frame)
                cv2.waitKey(5)

                # 接近の判定
                area = w * h # 矩形の面積
                frame_size = (frame.shape[0] * frame.shape[1]) # 元の画像の大きさを取得
                if area > (frame_size / 4): # 矩形の面積が取得画像の1/4より大きければ接近と判定
                    self.drone.approach_flag = True
                    print("被災者に接近")
                    break


                # キー入力による制御
                if key == 27:                   # k が27(ESC)だったらwhileループを脱出，プログラム終了
                break
                elif key == ord('t'):
                    drone.takeoff()             # 離陸
                elif key == ord('l'):
                    flag = 0    # フィードバックOFF
                    drone.send_command('rc 0 0 0 0')    # ラジコン指令をゼロに
                    drone.land()    # 着陸
                    time.sleep(3)   # 着陸するまで他のコマンドを打たないよう，ウェイトを入れる
                elif key == ord('w'):
                    drone.move_forward(0.3)     # 前進
                elif key == ord('s'):
                    drone.move_backward(0.3)    # 後進
                elif key == ord('a'):
                    drone.move_left(0.3)        # 左移動
                elif key == ord('d'):
                    drone.move_right(0.3)       # 右移動
                elif key == ord('q'):
                    drone.rotate_ccw(20)        # 左旋回
                elif key == ord('e'):
                    drone.rotate_cw(20)         # 右旋回
                elif key == ord('r'):
                    drone.move_up(0.3)          # 上昇
                elif key == ord('f'):
                    drone.move_down(0.3)        # 下降
                elif key == ord('1'):
                    flag = 1                    # フィードバック制御ON
                elif key == ord('2'):
                    flag = 0                    # フィードバック制御OFF
                    drone.send_command('rc 0 0 0 0')    # ラジコン指令をゼロに

                # (Z)5秒おきに'command'を送って、死活チェックを通す
                current_time = time.time()  # 現在時刻を取得
                if current_time - pre_time > 5.0 :  # 前回時刻から5秒以上経過しているか？
                    drone.send_command('command')   # 'command'送信
                    pre_time = current_time         # 前回時刻を更新


            else: # トラッカーの更新に失敗，人が検知できなかった場合
                self.drone.detect_flag　= False
                print("追跡失敗…")
                break
            
        except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
            print( "SIGINTを検知" )