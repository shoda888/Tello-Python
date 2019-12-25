import csv
import math

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
neaaa = [float(s) for s in data["1"]];
rsho = [float(v) for v in data["2"]];
relb = [float(v) for v in data["3"]];
lsho = [float(v) for v in data["5"]];
lelb = [float(v) for v in data["6"]];
rhip = [float(v) for v in data["8"]];
lhip = [float(v) for v in data["9"]];

#ベクトルの角度を計算
def vec_angle(v1,v2):
    v1length = math.sqrt(pow(v1[0],2)+pow(v1[1],2));
    v2length = math.sqrt(pow(v2[0],2)+pow(v2[1],2));
    in_pro = v1[0]*v2[0] + v1[1]*v2[1];
    cos = in_pro/(v1length*v2length);
    theta = math.degrees(math.acos(cos));

    return theta
