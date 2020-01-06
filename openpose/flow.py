from mutagen.mp3 import MP3 as mp3
import pygame
import time
import csv

def play(filename):  # MP3を再生，3回再生
    pygame.mixer.init()
    pygame.mixer.music.load(filename)  # 音源読み込み
    mp3_length = mp3(filename).info.length  # 音源の長さ取得
    pygame.mixer.music.play(3)  # 再生回数指定
    time.sleep(mp3_length * 3 + 0.25)  # 再生回数指定時長さ変更，再生開始後音源の長さ待機(0.25s誤差解消)
    pygame.mixer.music.stop()  # 再生停止


def read_dict(file):
    with open(file, newline = "") as f:
        read_dict = csv.DictReader(f, delimiter=",", quotechar='"')
        ks = read_dict.fieldnames
        return_dict = {k: [] for k in ks}

        for row in read_dict:
            for k, v in row.items():
                return_dict[k].append(v) # notice the type of the value is always string.

    return return_dict


def wri(file,pr):
    with open(file, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([pr])


data = read_dict("label.csv")
labeldata = data["label"]
data = read_dict("state.csv")
statedata = data["state"]


#アナウンス(state=1,2の場合)
#state1:「片腕下げて」
if statedata[-1] == "1":
    play("kataude_down.mp3")
    #アナウンス直後(state3)に遷移
    wri("state.csv",3)
elif statedata[-1] == "2":
    play("ryoude_up.mp3")
    #アナウンス直後(state4)に遷移
    wri("state.csv",4)


#対象の姿勢が一定時間同様だった場合#############################################################################
if labeldata[-1] == labeldata[-2] and labeldata[-2] == labeldata[-3] and labeldata[-3] == labeldata[-4]:

    #近づいた直前(state=0)，両腕を上げているかどうか確認
    if statedata[-1] == "0":
        #両腕を上げていた場合，「片腕下げて」のアナウンス直前の状態(state=1)に遷移
        if labeldata[-1] == "2":
            wri("state.csv",1)
        #両腕を下げていた場合，「両腕上げて」のアナウンス直前の状態(state=2)に遷移
        else:
            wri("state.csv",2)

    #「片腕下げて」アナウンス直後(state=3)の場合
    if statedata[-1] == "3":
        #左腕のみor右腕のみ上げている場合
        if labeldata[-1] == "1" or labeldata == "0":
            #避難勧告(yobikake.csvの値が0である場合，避難勧告とする)
            wri("yobikake.csv",0)
        else:
            #救助要請(yobikake.csvの値が1である場合，救助要請とする)
            wri("yobikake.csv",1)

    #「両腕上げて」アナウンス直後(state=4)の場合
    if statedata[-1] == "4":
        #両腕上げていた場合
        if labeldata[-1] == "2":
            #避難勧告
            wri("yobikake.csv",0)
            wri("state.csv",0)
        #そうでない場合
        else:
            #救助要請
            wri("yobikake.csv",1)
            wri("state.csv",0)
##################################################################################################


#play('kataude_down.mp3')
#play('ryoude_up.mp3')
