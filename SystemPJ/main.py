#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tello import Tello		# tello.pyをインポート
import time			# time.sleepを使いたいので
import cv2			# OpenCVを使うため
import sys
import os
from absl import app

# こんな感じでimportするようにしよう
sys.path.append('./ProcessVoice')
sys.path.append('./ProcessImage')
sys.path.append('./rec_human')
sys.path.append('../openpose')

# import *
import speak
import run_load_human_model
import run_function
from defaultModule import Default
from approachModule import Approach
import os 




# ドローンのstatus定義
# 'default': ホバリングする(初期状態)
# 'approach': 人を検知し，近づく
# 'communicate': 対話状態
# 'judingpose': 姿勢検知

# メイン関数
def main(_argv):
	# Telloクラスを使って，droneというインスタンス(実体)を作る
	drone = Tello('', 8889, command_timeout=.01)  

	# 人検知，接近用のインスタンス，フラグ，トラッカータイプ
	default = Default(drone) # 人探索用のインスタンス作成
	

	# track_type = "KCF" # トラッカーのタイプ，ユーザーが指定

	# 処理の開始
	drone.send_command('command') # SDKモードを開始

	current_time = time.time()	# 現在時刻の保存変数
	pre_time = current_time		# 5秒ごとの'command'送信のための時刻変数

	drone.subscribe() # 対話開始
	
	# ここでアレクサに「救助アプリを開いて」と言うと離陸し対話を受け付ける

	# 強制離陸する場合
	# drone.takeoff()
	
	
	time.sleep(0.5)		# 通信が安定するまでちょっと待つ

	# drone.takeoff() # 自動で離陸しているが，ここはAlexaを使用して離陸させた方が良いかも(対話を開始するタイミングをトリガーさせるためにも)
	
	# openpose_flag = 0:
	#Ctrl+cが押されるまでループ
	try:
		while True:

			if drone.start_flag:


				if drone.status == 'default':
					# デフォルト状態でホバリングし，常に人を認識する．認識した時，statusを'approach'に変更する
					print(drone.status)

					frame, bbox = default.detect() # 人を探し，検知したら領域をbboxに保存

					if drone.detect_flag: # 人を検知後statusをapproachに変更
						drone.to_communicate() 
						approach = Approach(drone, frame, bbox) # Approachクラスのインスタンスを作成，トラッカーの初期化
						continue
					
					# デバッグ用
					# time.sleep(1)
					# print(drone.status)
					# drone.to_approach()

				if drone.status == 'approach':
					# 認識した人に近づく．近づき終わったらstatusを'communicate'に変更する
					print(drone.status)
					approach.approach() # 検知した人を追跡．結果を返す

					# 人を追跡できているか，または接近できたかどうかの判定
					if drone.detect_flag and drone.approach_flag: # 接近できていればstatusをcommunicateへ変更
						# drone.to_communicate()
						break
					elif not drone.detect_flag: # 追跡が失敗したらdefaultへ戻る
						drone.to_default()
						del approach # Approachクラスのインスタンスを削除
					else: # 例外処理
						print("なんかエラーっぽいよ")
						print("detect:" + str(drone.detect_flag))
						print("approach:" + str(drone.approach_flag))
						time.sleep(10)


					# デバッグ用
					# time.sleep(1)
					# drone.to_communicate()
         

				if drone.status == 'communicate':
					# 人と対話する．対話が正常終了したらstatusを'default'に戻す．対話に失敗した場合はstatusを'judingpose'に
					speak.mp3play('./ProcessVoice/speech_20191223054237114.mp3')

					# デバッグ用
					# drone.to_default()
					# drone.to_judingpose()
										
					# 対話時間
					time.sleep(5)
					drone.send_command('command')	# 'command'送信
					time.sleep(5)
					drone.send_command('command')	# 'command'送信
					time.sleep(5)
					drone.send_command('command')	# 'command'送信

					if drone.status == 'communicate': # 無言だった場合
						drone.status = 'judingpose' # 人の姿勢を検出する
					

				if drone.status == 'judingpose':
				  	# 人の姿勢を検出する．姿勢推定を行い人の状態の判定後，人に話しかけ，statusを'default'に戻す
					speak.mp3play('../openpose/jirikidehinanndekinai.mp3')
					time.sleep(1)
					speak.mp3play('../openpose/jirikidehinanndekiru.mp3')
					time.sleep(1)

					while True:
						frame = drone.read()	# 映像を1フレーム取得
						if frame is None or frame.size == 0:	# 中身がおかしかったら無視
							continue 

						# (B)ここから画像処理
						image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # OpenCV用のカラー並びに変換する
						small_image = cv2.resize(image, dsize=(480,360) )	# 画像サイズを半分に変更

						run_function.openpose(small_image)
						if run_load_human_model.add_label("../openpose/uncho.csv") == 3:
							speak.mp3play('../openpose/hinansitekudasai.mp3')
						else:
							speak.mp3play('../openpose/kyuujyowoyobimasu.mp3')

					
					# デバッグ用
					time.sleep(1)
					print(drone.status)
					drone.to_default()
					

			# 以下(X)(Y)(Z)は便宜的に記載した．システムで必要な処理ではない

			# (X)ウィンドウに表示
			# cv2.imshow('OpenCV Window', small_image)	# ウィンドウに表示するイメージを変えれば色々表示できる

			# (Y)OpenCVウィンドウでキー入力を1ms待つ
			# key = cv2.waitKey(1)
			# if key == 27:					# k が27(ESC)だったらwhileループを脱出，プログラム終了
			# 	break
			# elif key == ord('t'):
			# 	drone.takeoff()				# 離陸
			# elif key == ord('l'):
			# 	drone.land()				# 着陸
			# elif key == ord('w'):
			# 	drone.move_forward(0.3)		# 前進
			# elif key == ord('s'):
			# 	drone.move_backward(0.3)	# 後進
			# elif key == ord('a'):
			# 	drone.move_left(0.3)		# 左移動
			# elif key == ord('d'):
			# 	drone.move_right(0.3)		# 右移動
			# elif key == ord('q'):
			# 	drone.rotate_ccw(20)		# 左旋回
			# elif key == ord('e'):
			# 	drone.rotate_cw(20)			# 右旋回
			# elif key == ord('r'):
			# 	drone.move_up(0.3)			# 上昇
			# elif key == ord('f'):
			# 	drone.move_down(0.3)		# 下降
			# elif key == ord('o'):
			# 	image_path = "../openpose/images/"  # openpose
			# 	image = cv2.imwrite(image_path+"input.jpg",small_image) 
			# 	os.system('python ../openpose/openpose.py') 


			# (Z)5秒おきに'command'を送って、死活チェックを通す
			current_time = time.time()	# 現在時刻を取得
			if current_time - pre_time > 5.0 :	# 前回時刻から5秒以上経過しているか？
				drone.send_command('command')	# 'command'送信
				pre_time = current_time			# 前回時刻を更新


	except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
		print( "SIGINTを検知" )

	# telloクラスを削除
	drone.land()
	del drone


# "python main.py"として実行された時だけ動く様にするおまじない処理
if __name__ == "__main__":		# importされると"__main__"は入らないので，実行かimportかを判断できる．
	try:
		app.run(main)
	except SystemExit:
		pass
