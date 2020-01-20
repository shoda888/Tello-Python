# -*- coding: utf-8 -*-
import boto3
import time         # time.sleepを使いたいので
import cv2          # OpenCVを使うため

class Rekog:
    def __init__(self, drone):
        self.drone = drone
        self.client = boto3.client('rekognition','ap-northeast-1')
    
    def catch(self):

        flag = 1
        current_time = time.time()  # 現在時刻の保存変数
        pre_time = current_time     # 5秒ごとの'command'送信のための時刻変数

        cnt_frame = 0   # フレーム枚数をカウントする変数

        #Ctrl+cが押されるまでループ
        try:
            while True:

                # (A)画像取得
                drone = self.drone
                frame = drone.read()    # 映像を1フレーム取得
                if frame is None or frame.size == 0:    # 中身がおかしかったら無視
                    continue 

                pre_faces = False  # 顔検出結果を格納する変数

                # (B)ここから画像処理
                image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する
                small_image = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更

                cv_image = small_image  # ウィンドウ表示画像の名前はcv_imageにする

                cnt_frame += 1  # フレームを+1枚
                # 5フレームに１回顔認識処理をする
                if cnt_frame >= 5:
                    ret, buf = cv2.imencode('.jpg', cv_image)

                    # 人検出
                    # rekognitionのdetect_labelsにバイト列を渡してラベル検出実行
                    response = self.client.detect_labels(
                                Image={
                                    'Bytes': buf.tobytes()
                                }
                    )

                    # print response["Labels"][0]["Name"]
                    for label in response["Labels"]:
                        # print(label)
                        if label["Name"] == 'Person':
                            # いちばんデカイ矩形を採用する処理を書く
                            area = []
                            for i in range(len(label["Instances"])):
                                yoko = label["Instances"][i]["BoundingBox"]["Width"]
                                tate = label["Instances"][i]["BoundingBox"]["Height"]
                                area.append(yoko * tate)
                            faces = label["Instances"][area.index(max(area))]["BoundingBox"]

                    # 検出結果を格納
                    pre_faces = faces

                    cnt_frame = 0   # フレーム枚数をリセット


                if pre_faces: # 人があるなら続けて処理
                    # 検出した人に枠を書く
                    x = int(pre_faces['Left'] * 480)
                    y = int(pre_faces['Top'] * 360)
                    w = int(pre_faces['Width'] * 480)
                    h = int(pre_faces['Height'] * 360)
                    cv2.rectangle(cv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # １個めの顔のx,y,w,h,顔中心cx,cyを得る
                    # x = pre_faces[0][0]
                    # y = pre_faces[0][1]
                    # w = pre_faces[0][2]
                    # h = pre_faces[0][3]
                    cx = int( x + w/2 )
                    cy = int( y + h/2 )

                    # 自動制御フラグが1の時だけ，Telloを動かす
                    if flag == 1:
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

                        # アプローチステータスに変更
                        # drone.to_approach()


                # (X)ウィンドウに表示
                cv2.imshow('OpenCV Window', cv_image)   # ウィンドウに表示するイメージを変えれば色々表示できる

                # (Y)OpenCVウィンドウでキー入力を1ms待つ
                key = cv2.waitKey(1)
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

        except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
            print( "SIGINTを検知" )

            drone.send_command('streamoff')
            # telloクラスを削除
            del drone
