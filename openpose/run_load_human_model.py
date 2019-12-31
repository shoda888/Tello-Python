import csv
import math
import numpy as np

def read_dict(file):
    with open(file, newline = "") as f:
        read_dict = csv.DictReader(f, delimiter=",", quotechar='"')
        ks = read_dict.fieldnames
        return_dict = {k: [] for k in ks}

        for row in read_dict:
            for k, v in row.items():
                return_dict[k].append(v) # notice the type of the value is always string.

    return return_dict


data = read_dict("uncho.csv")
#1:首，2:右肩，3:右肘，5:左肩，6:左肘，8:右尻，11:左尻
neck = [float(s) for s in data["1"]];
neck = np.array(neck[0:2]);
rsho = [float(v) for v in data["2"]];
rsho = np.array(rsho[0:2]);
relb = [float(v) for v in data["3"]];
relb = np.array(relb[0:2]);
lsho = [float(v) for v in data["5"]];
lsho = np.array(lsho[0:2]);
lelb = [float(v) for v in data["6"]];
lelb = np.array(lelb[0:2]);
rhip = [float(v) for v in data["8"]];
rhip = np.array(rhip[0:2]);
lhip = [float(v) for v in data["11"]];
lhip = np.array(lhip[0:2]);

#ベクトルの設定
#p1:首から右尻，p2:首から左尻，p3:右肩から右肘，p4:左肩から左肘
p1 = neck - rhip;
p2 = neck - lhip;
p3 = rsho - relb;
p4 = lsho - lelb;

#ベクトルの角度を計算
def vec_angle(v1,v2):
    v1length = math.sqrt(pow(v1[0],2)+pow(v1[1],2));
    v2length = math.sqrt(pow(v2[0],2)+pow(v2[1],2));
    in_pro = v1[0]*v2[0] + v1[1]*v2[1];
    cos = in_pro/(v1length*v2length);
    theta = math.degrees(math.acos(cos));

    return theta

#右腕，左腕の角度
rang = vec_angle(p1,p3);
lang = vec_angle(p2,p4);

if rang >= 90 and lang < 90:
    #右手のみ挙げている場合(label=0)
    label = 0;
elif rang < 90 and lang >= 90:
    #左手のみ挙げている場合(label=1)
    label = 1;
else:
    #右手も左手も挙げている場合(label=2)
    label = 2;


with open('label.csv', 'a', newline="") as f:
    writer = csv.writer(f)
    writer.writerow([label])
