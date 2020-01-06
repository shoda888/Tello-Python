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


data = read_dict("label.csv")

labeldata = data["label"]
statedata = data["state"]

if labeldata[-1] == labeldata[-2] and labeldata[-2] == labeldata[-3] and labeldata[-3] == labeldata[-4]:
    if labeldata[-1] == "2":
        a = 21




#play('kataude_down.mp3')
#play('ryoude_up.mp3')

print(a)
